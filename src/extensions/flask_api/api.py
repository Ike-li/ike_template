import uuid
from functools import wraps

from flask import Blueprint, Response
from flask import current_app as app
from flask import g, jsonify, request
from flask.views import MethodView, MethodViewType
from marshmallow import ValidationError

from extensions.flask_api.exceptions import APIException, PermissionDenied
from extensions.sentry import sentry


def ok_response(result):
    """成功的 response"""
    new_body = {"ok": True, "result": result}
    return jsonify(new_body)


def failed_response(error_type, error_message, error_data=None):
    """失败的 response"""
    body = {
        "ok": False,
        "error_type": error_type,
        "error_message": error_message
    }
    if error_data is not None:
        body["error_data"] = error_data
    return jsonify(body)


def validation_error_response(validation_error):
    """字段验证失败的 response
    validation_error: ValidationError
    """
    errors = list()

    if validation_error.messages.get("_schema"):
        # 自定义的一些错误
        errors.append({
            "error_type": "validation_error",
            "field": "_schema",
            "message": validation_error.messages.get("_schema")[0],
        })

    for field in validation_error.messages:
        if isinstance(validation_error.messages[field], dict):
            message = "Invalid data format"
        else:
            message = validation_error.messages[field][0]
        field_error = {
            "error_type": "validation_error",
            "field": field,
            "message": message,
        }
        errors.append(field_error)

    new_body = {
        "ok": False,
        "error_type": "data_validation_errors",
        "error_message": "Data has validation errors",
        "errors": errors,
    }
    return jsonify(new_body)


def route(blueprint: Blueprint, rule, **options):
    """函数 view 的路由"""

    def wrapper(view):

        @wraps(view)
        def decorator(*args, **kwargs):
            """处理错误响应"""
            try:
                result = view(*args, **kwargs)
            except Exception as exception:
                return handle_exception(view.__name__, exception, **kwargs)
            else:
                if isinstance(result, Response):
                    return result

                return ok_response(result)

        # Flask 的 endpoint, 用于 url_for(endpoint) 获取 endpoint 对应的 url rule
        endpoint = options.pop("endpoint", decorator.__name__)
        blueprint.add_url_rule(rule, endpoint, view_func=decorator, **options)
        return decorator

    return wrapper


def class_route(blueprint: Blueprint, rule, **options):
    """class view 的路由"""

    def decorator(view):
        if isinstance(view, MethodViewType):
            view_func = view.as_view(view.__name__)
        else:
            view_func = view

        blueprint.add_url_rule(
            rule, view.__name__, view_func=view_func, **options
        )
        return view

    return decorator


def handle_exception(view_name, exception, **kwargs):
    """处理异常
    APIException: 返回适当的错误信息
    else: 重新抛出异常
    """
    if isinstance(exception, ValidationError):
        return validation_error_response(exception)
    elif hasattr(exception,
                 "error_type") and hasattr(exception, "error_message"):
        error_data = getattr(exception, "error_data", None)
        return failed_response(
            error_type=exception.error_type,
            error_message=exception.error_message,
            error_data=error_data,
        )
    else:
        # 非 debug 模式下, 发送错误消息到 sentry
        if not app.config["DEBUG"]:
            with sentry.context:
                sentry.extra_context(kwargs)
                sentry.tags_context({"API": view_name})
                sentry.captureException()
        raise exception


def login_required(view):
    """限制为登录才能访问, 即提供 x-authenticated-userid Header 才能访问"""

    @wraps(view)
    def decorator(*args, **kwargs):
        user_id = request.headers.get("x-authenticated-userid", None)
        if user_id is None:
            raise PermissionDenied
        g.user_id = uuid.UUID(user_id)
        return view(*args, **kwargs)

    return decorator


class APIBaseView(MethodView):
    """扩展 class based view, 增加异常处理"""

    @property
    def kong_user_id(self):
        user_id = request.headers.get("x-authenticated-userid", None)
        if user_id:
            return uuid.UUID(user_id)

    @property
    def kong_admin_id(self):
        return request.headers.get("x-authenticated-userid", None)

    @property
    def app_id(self):
        # 暂时如果app id不传的话，就是来玩，等客户端慢慢升级
        app_id = request.headers.get("App-Id")
        if app_id:
            return app_id
        else:
            raise APIException(
                error_type="app_id_not_found", error_message="App-Id not found"
            )

    @classmethod
    def parse_json(cls):
        """解析 request body 为 json"""
        return request.json or {}

    def dispatch_request(self, *args, **kwargs):
        try:
            return super().dispatch_request(*args, **kwargs)
        except Exception as exception:
            return handle_exception(
                self.__class__.__name__, exception, **kwargs
            )
