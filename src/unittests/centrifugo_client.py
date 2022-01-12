# pylava: skip=1
"""
用于测试的 centrifugo 客户端
"""
import asyncio
import json
import logging
import random
import uuid

import jwt
import websockets
from flask import current_app

logger = logging.getLogger("centrifuge")


class CentrifugeException(Exception):
    """
    CentrifugeException is a base exception for all other exceptions
    in this library.
    """

    pass


class ConnectionClosed(CentrifugeException):
    """
    ConnectionClosed raised when underlying websocket connection closed.
    """

    pass


class Timeout(CentrifugeException):
    """
    Timeout raised every time operation times out.
    """

    pass


class SubscriptionError(CentrifugeException):
    """
    SubscriptionError raised when an error subscribing on channel occurred.
    """

    pass


class CallError(CentrifugeException):
    pass


class Subscription:
    """
    Subscription describes client subscription to Centrifugo channel.
    """

    def __init__(self, client, channel, **kwargs):
        self._future = asyncio.Future()
        self._subscribed = False
        self.client = client
        self.channel = channel
        self.last_message_id = None
        self.handlers = {
            "message": kwargs.get("on_message"),
            "subscribe": kwargs.get("on_subscribe"),
            "unsubscribe": kwargs.get("on_unsubscribe"),
            "error": kwargs.get("on_error"),
        }

    async def unsubscribe(self):
        await self.client._unsubscribe(self)

    async def subscribe(self):
        await self.client._resubscribe(self)

    async def publish(self, data):
        success = await self.client._publish(self, data)
        return success


STATUS_CONNECTED = "connected"
STATUS_CONNECTING = "connecting"
STATUS_DISCONNECTED = "disconnected"


class Client:
    """
    Client is a Centrifugo server websocket client.
    """

    factor = 2
    base_delay = 1
    max_delay = 60
    jitter = 0.5
    private_channel_prefix = "$"

    def __init__(self, address, token, **kwargs):
        self.address = address
        self.token = token
        self.status = STATUS_DISCONNECTED
        self.client_id = None
        self._message_id = 0
        self._history = {}
        self._conn = None
        self._subs = {}
        self._messages = asyncio.Queue()
        self._delay = 1
        self._reconnect = kwargs.get("reconnect", True)
        self._ping = kwargs.get("ping", True)
        self._ping_timeout = kwargs.get("ping_timeout", 25)
        self._pong_wait_timeout = kwargs.get("pong_wait_timeout", 5)
        self._ping_timer = None
        self._future = None
        self._handlers = {
            "connect": kwargs.get("on_connect"),
            "disconnect": kwargs.get("on_disconnect"),
            "error": kwargs.get("on_error"),
            "private_sub": kwargs.get("on_private_sub"),
        }
        self._loop = kwargs.get("loop", asyncio.get_event_loop())
        self._futures = {}
        self._tasks = set()

    def channels(self):
        return self._subs.keys()

    async def close(self):
        if self._conn is None:
            return
        try:
            await self._conn.close()
            for task in self._tasks:
                task.cancel()
        except websockets.ConnectionClosed:
            pass

    def _exponential_backoff(self, delay):
        delay = min(delay * self.factor, self.max_delay)
        return delay + random.randint(0, int(delay * self.jitter))

    async def reconnect(self):
        if self.status == STATUS_CONNECTED:
            return

        if self._conn and self._conn.open:
            return

        if not self._reconnect:
            logger.debug("centrifuge: won't reconnect")
            return

        logger.debug("centrifuge: start reconnecting")

        self.status = STATUS_CONNECTING

        self._delay = self._exponential_backoff(self._delay)
        await asyncio.sleep(self._delay)
        success = await self._create_connection()
        if success:
            success = await self._subscribe(self._subs.keys())

        if not success:
            asyncio.ensure_future(self.reconnect())

    def _get_message(self, method, params):
        self._message_id += 1
        message = {"id": self._message_id, "method": method, "params": params}
        self._history[self._message_id] = method
        return message

    async def _create_connection(self):
        try:
            self._conn = await websockets.connect(self.address)
        except OSError:
            return False
        self._delay = self.base_delay
        params = {
            "token": self.token,
            "data": {},
        }
        message = self._get_message("connect", params)
        try:
            await self._conn.send(json.dumps(message))
        except websockets.ConnectionClosed:
            return False
        asyncio.ensure_future(self._listen())
        self._tasks.add(asyncio.ensure_future(self._process_messages()))

        self._future = asyncio.Future()
        success = await self._future
        if success:
            if self._ping:
                self._ping_timer = self._loop.call_later(
                    self._ping_timeout,
                    lambda: asyncio.
                    ensure_future(self._send_ping(), loop=self._loop),
                )
            handler = self._handlers.get("connect")
            if handler:
                await handler(**{"client_id": self.client_id})

        return True

    async def _send_ping(self):
        if self.status != STATUS_CONNECTED:
            return
        uid = uuid.uuid4().hex
        message = self._get_message("ping", {})

        try:
            await self._conn.send(json.dumps(message))
        except websockets.ConnectionClosed:
            return

        future = self._register_future(uid, self._pong_wait_timeout)
        try:
            await future
        except Timeout:
            await self._disconnect("no ping", True)

    async def connect(self):
        self.status = STATUS_CONNECTING
        success = await self._create_connection()
        if not success:
            asyncio.ensure_future(self.reconnect())

    async def disconnect(self):
        await self.close()

    async def subscribe(self, channel, **kwargs):
        sub = Subscription(self, channel, **kwargs)
        self._subs[channel] = sub
        await self._subscribe(channel)
        return sub

    async def _subscribe(self, channel):
        params = {"channel": channel}
        message = self._get_message("subscribe", params)

        if not self._conn:
            return False

        try:
            await self._conn.send(json.dumps(message))
        except websockets.ConnectionClosed:
            return False

        return True

    async def _resubscribe(self, sub):
        self._subs[sub.channel] = sub
        asyncio.ensure_future(self._subscribe([sub.channel]))
        return sub

    async def _unsubscribe(self, sub):
        if sub.channel in self._subs:
            del self._subs[sub.channel]

        message = self._get_message("unsubscribe", {"channel": sub.channel})

        unsubscribe_handler = sub.handlers.get("unsubscribe")
        if unsubscribe_handler:
            await unsubscribe_handler(**{"channel": sub.channel})

        try:
            await self._conn.send(json.dumps(message))
        except websockets.ConnectionClosed:
            pass

    def _register_future(self, uid, timeout):
        future = asyncio.Future()
        self._futures[uid] = future

        if timeout:

            def cb():
                if not future.done():
                    future.set_exception(Timeout)
                    del self._futures[uid]

            self._loop.call_later(timeout, cb)

        return future

    def _future_error(self, uid, error):
        future = self._futures.get(uid)
        if not future:
            return
        future.set_exception(CallError(error))
        del self._futures[uid]

    def _future_success(self, uid, result):
        future = self._futures.get(uid)
        if not future:
            return
        future.set_result(result)
        del self._futures[uid]

    async def _publish(self, sub, data):
        if sub.channel not in self._subs:
            raise CallError("subscription not in subscribed state")

        await sub._future

        uid = uuid.uuid4().hex
        message = self._get_message(
            "publish", {
                "channel": sub.channel,
                "data": data
            }
        )

        try:
            await self._conn.send(json.dumps(message))
        except websockets.ConnectionClosed:
            raise ConnectionClosed

        future = self._register_future(uid, 0)
        result = await future
        return result

    async def _disconnect(self, reason, reconnect):
        if self._ping_timer:
            self._ping_timer.cancel()
            self._ping_timer = None
        if not reconnect:
            self._reconnect = False
        if self.status == STATUS_DISCONNECTED:
            return
        self.status = STATUS_DISCONNECTED
        self.client_id = None
        await self.close()

        for ch, sub in self._subs.items():
            sub._future = asyncio.Future()
            unsubscribe_handler = sub.handlers.get("unsubscribe")
            if unsubscribe_handler:
                await unsubscribe_handler(**{"channel": sub.channel})

        handler = self._handlers.get("disconnect")
        if handler:
            await handler(**{"reason": reason, "reconnect": reconnect})
        asyncio.ensure_future(self.reconnect())

    async def _process_connect(self, response):
        body = response.get("result")
        self.client_id = body.get("client")
        if body.get("error"):
            if self._future:
                self._future.set_result(False)
            await self.close()
            handler = self._handlers.get("error")
            if handler:
                await handler()
        else:
            self.status = STATUS_CONNECTED
            if self._future:
                self._future.set_result(True)

    async def _process_subscribe(self, response):
        body = response.get("result", {})
        channel = body.get("channel")

        sub = self._subs.get(channel)
        if not sub:
            return

        error = response.get("error")
        if not error:
            sub._future.set_result(True)
            subscribe_handler = sub.handlers.get("subscribe")
            if subscribe_handler:
                await subscribe_handler(**{"channel": channel})
            msg_handler = sub.handlers.get("message")
            messages = body.get("messages", [])
            if msg_handler and messages:
                for message in messages:
                    sub.last_message_id = message.get("uid")
                    await msg_handler(**message)
        else:
            sub._future.set_exception(SubscriptionError(error))
            error_handler = sub.handlers.get("error")
            if error_handler:
                kw = {
                    "channel": channel,
                    "error": error,
                    "advice": response.get("advice", ""),
                }
                await error_handler(**kw)

    async def _process_message(self, response):
        body = response.get("result")
        sub = self._subs.get(body.get("channel"))
        if not sub:
            return
        handler = sub.handlers.get("message")
        if handler:
            await handler(**body)

    async def _process_publish(self, response):
        uid = response.get("uid")
        if not uid:
            return

        error = response.get("error")
        if error:
            self._future_error(uid, error)
        else:
            self._future_success(
                uid,
                response.get("result", {}).get("status", False)
            )

    async def _process_ping(self, response):
        uid = response.get("uid")
        if not uid:
            return

        error = response.get("error")
        if error:
            self._future_error(uid, error)
        else:
            self._future_success(
                uid,
                response.get("result", {}).get("data", "")
            )

    async def _process_disconnect(self, response):
        logger.debug("centrifuge: disconnect received")
        body = response.get("result", {})
        reconnect = body.get("reconnect")
        reason = body.get("reason", "")
        await self._disconnect(reason, reconnect)

    async def _process_response(self, response):
        # Restart ping timer every time we received something from connection.
        # This allows us to reduce amount of pings sent around in busy apps.
        if self._ping_timer:
            self._ping_timer.cancel()
            self._ping_timer = self._loop.call_later(
                self._ping_timeout,
                lambda: asyncio.
                ensure_future(self._send_ping(), loop=self._loop),
            )

        method = self._history.get(response.get("id", 0), None)
        call_back = None
        if method is None:
            call_back = self._process_message
        elif method == "connect":
            call_back = self._process_connect
        elif method == "subscribe":
            call_back = self._process_subscribe
        elif method == "disconnect":
            call_back = self._process_disconnect
        elif method == "publish":
            call_back = self._process_publish
        elif method == "ping":
            call_back = self._process_ping
        if call_back:
            await call_back(response)
        else:
            logger.debug(
                "centrifuge: received message with unknown method %s", method
            )

    async def _parse_response(self, message):
        try:
            response = json.loads(message)
            if isinstance(response, dict):
                await self._process_response(response)
            if isinstance(response, list):
                for obj_response in response:
                    await self._process_response(obj_response)
        except json.JSONDecodeError as err:
            logger.error("centrifuge: %s", err)

    async def _process_messages(self):
        logger.debug("centrifuge: start message processing routine")
        while True:
            if self._messages:
                message = await self._messages.get()
                await self._parse_response(message)

    async def _listen(self):
        logger.debug("centrifuge: start message listening routine")
        while self._conn.open:
            try:
                result = await self._conn.recv()
                if result:
                    logger.debug(f"centrifuge: data received, {result}")
                    await self._messages.put(result)
            except websockets.ConnectionClosed:
                break

        logger.debug("centrifuge: stop listening")

        reason = ""
        reconnect = True
        if self._conn.close_reason:
            try:
                data = json.loads(self._conn.close_reason)
            except ValueError:
                pass
            else:
                reconnect = data.get("reconnect", True)
                reason = data.get("reason", "")

        await self._disconnect(reason, reconnect)


class CentrifugoClient:
    """
    用户跑测试的 websocket 会话
    eg:
        async with WebsocketClient(ws_url, user_id) as session:
            pass
    """

    def __init__(
        self,
        user_id=None,
        public_channel_id=None,
        channel_name="user",
        server_path="/connection/websocket",
    ):

        # 要不就是私人频道，要不就是公共频道
        assert user_id or public_channel_id

        self.messages = []

        if user_id:
            self.user_id = str(user_id)
            self.channel = f"{channel_name}#{self.user_id}"
        else:
            self.user_id = str(uuid.uuid4())
            self.channel = f"{channel_name}|{public_channel_id}"

        token = jwt.encode({"sub": self.user_id}, "mytestsecret").decode()
        centrifugo_url = current_app.config["CENTRIFUGO_URL"]
        centrifugo_ws_url = centrifugo_url.replace("http", "ws") + server_path
        self._client = Client(centrifugo_ws_url, token, reconnect=False)

    async def on_message(self, **message):
        print(f"Received message: {message}")
        self.messages.append(message)

    async def __aenter__(self):
        await asyncio.wait_for(self._client.connect(), 10)
        await self._client.subscribe(self.channel, on_message=self.on_message)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        counter = 0
        while not self.messages:
            await asyncio.sleep(0.1)

            counter += 0.1
            if 10 < counter:
                break

        await self._client.close()
