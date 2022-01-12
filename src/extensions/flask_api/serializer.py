from functools import wraps

from flask import g, request


def serialize(serializer, many=False):
    """使用指定 serializer 来序列化数据, 并返回为 json 格式"""

    def wrapper(view):

        @wraps(view)
        def decorator(*args, **kwargs):
            response_object = view(*args, **kwargs)
            return serializer(many=many).dump(response_object)

        return decorator

    return wrapper


def validate(validator):
    """使用 Marshmallow 来验证请求数据是否合法"""

    def wrapper(view):

        @wraps(view)
        def decorator(*args, **kwargs):
            # 反序列化请求数据
            request_data = request.json if request.json is not None else {}

            # 处理 GET 参数的格式，让 marshmallow 比较容易处理
            for key, value in request.args.items():
                if isinstance(value, list) and len(value) == 1:
                    request_data[key] = value[0]
                else:
                    request_data[key] = value

            request_data.update(kwargs)
            g.validated_data = validator().load(request_data)
            return view()

        return decorator

    return wrapper
