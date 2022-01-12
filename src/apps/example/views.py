from datetime import datetime

import ujson
from flask import Blueprint
from flask import current_app as app
from flask import g
from flask_babel import gettext as _

from apps.example.models import Person
from apps.example.serializers import (
    FirstNameValidator,
    PersonSerializer,
    PersonValidator,
)
from extensions.centrifugo import centrifugo, user_channel
from extensions.flask_api.api import class_route, login_required, route
from extensions.flask_api.exceptions import ObjectNotFound
from extensions.flask_api.serializer import serialize, validate
from extensions.flask_api.views import (
    GetView,
    PostView,
    deprecated_api,
    removed_api,
)
from extensions.kafka import kafka_producer
from extensions.redis_cluster import redis_client, redis_lock

blueprint = Blueprint("example", __name__, url_prefix="/v1/example")


@route(blueprint, "/deprecated_function_view")
@deprecated_api
def deprecated_function_view_api():
    return "ok"


@class_route(blueprint, "/deprecated_class_view")
@deprecated_api
class DeprecatedView(GetView):

    def get_object(self):
        pass


@route(blueprint, "/removed_function_view")
@removed_api
def removed_function_view_api():
    return "ok"


@class_route(blueprint, "/removed_class_view")
@removed_api
class RemovedView(GetView):

    def get_object(self):
        pass


@route(blueprint, "/")
@serialize(PersonSerializer, many=True)
def person_list():
    """获取 Person list"""
    return Person.all()


@route(blueprint, "/<first_name>")
@validate(FirstNameValidator)
@serialize(PersonSerializer)
def get_person():
    """获取 Person list"""
    try:
        return Person.get(first_name=g.validated_data["first_name"])
    except Person.DoesNotExist:
        raise ObjectNotFound


@route(blueprint, "/", methods=["POST"])
@login_required
@validate(PersonValidator)
@serialize(PersonSerializer)
def create_person():
    """创建 Person"""

    with redis_lock(name="example-key", timeout=3):
        redis_client.set("example", "example")
        person = Person.create(
            first_name=g.validated_data["first_name"],
            last_name=g.validated_data["last_name"],
        )

        kafka_producer.send(
            app.config["FLASK_TEMPLATE_TOPIC"],
            ujson.dumps({
                "first_name": person.first_name,
                "last_name": person.last_name
            }).encode(),
        )
        return person


@class_route(blueprint, "/class/<first_name>")
class GetExampleView(GetView):
    args_deserializer_class = FirstNameValidator
    get_serializer_class = PersonSerializer

    def get_object(self):
        try:
            return Person.get(first_name=self.validated_data["first_name"])
        except Person.DoesNotExist:
            raise ObjectNotFound


@class_route(blueprint, "/class", methods=["POST"])
class PostExampleView(PostView):
    args_deserializer_class = PersonValidator
    post_serializer_class = PersonSerializer

    def save(self):
        """保存数据"""
        if self.app_id:
            print(_("You are using %(app_id)s", app_id=self.app_id))

        centrifugo.publish(
            user_channel(self.kong_user_id),
            {
                "stream": "example",
                "sent_at": datetime.utcnow().isoformat(),
                "payload": {
                    "action": "notify",
                    "message": self.validated_data,
                },
            },
        )

        return Person.create(
            first_name=self.validated_data["first_name"],
            last_name=self.validated_data["last_name"],
        )
