from functools import wraps

from flask import current_app as app
from flask import request
from flask.views import MethodViewType

from extensions.flask_api.api import APIBaseView, failed_response, ok_response
from extensions.flask_api.exceptions import APIException


class GetView(APIBaseView):
    """GET api view
    1. 获取数据对象
    2. 序列化数据
    """

    args_deserializer_class = None
    get_serializer_class = None

    def get(self, *args, **kwargs):
        """处理 GET 请求"""
        self.validated_data = self.get_validated_data(kwargs)
        target_object = self.get_object()
        serialized_data = self.serialize(target_object)
        return ok_response(serialized_data)

    @classmethod
    def parse_json(cls):
        """
        get 请求不解析body的数据, 客户端请求Get方法时不能传json，get的参数通过params传
        """
        return {}

    def get_validated_data(self, kwargs):
        # 反序列化请求数据
        if not self.args_deserializer_class:
            return {}

        request_data = self.parse_json()
        # 处理 GET 参数的格式，让 marshmallow 比较容易处理
        for key, value in request.args.items():
            if isinstance(value, list) and len(value) == 1:
                request_data[key] = value[0]
            else:
                request_data[key] = value
        request_data.update(kwargs)
        deserializer = self.args_deserializer_class()
        validated_data = deserializer.load(request_data)
        return validated_data

    def serialize(self, target_object):
        """序列化目标对象"""
        if not self.get_serializer_class:
            return {}
        data = self.get_serializer_class().dump(target_object)
        return data

    def get_object(self):
        """获取需要序列化的对象"""
        raise NotImplementedError


class PutView(APIBaseView):
    """更新已知资源 view
    1. 获取上下文: 通过数据库或其他 model 层获取数据
    2. 验证请求数据
    3. 保存数据
    """

    args_deserializer_class = None
    put_serializer_class = None

    def put(self, *args, **kwargs):
        self.request_data = kwargs
        self.validated_data = self.get_validated_data(kwargs)

        # 保存数据
        patched_object = self.save()
        return self.response(patched_object)

    def get_validated_data(self, kwargs):
        # 反序列化请求数据
        if not self.args_deserializer_class:
            return {}

        request_data = self.parse_json()
        request_data.update(kwargs)
        deserializer = self.args_deserializer_class()
        validated_data = deserializer.load(request_data)
        return validated_data

    def save(self):
        """根据 self.validated_data 和 self.context 保存数据到数据库"""
        raise NotImplementedError

    def response(self, saved_object):
        """响应结果
        默认返回空 json 对象, 需要修改则在子类中覆盖这个方法
        """
        if self.put_serializer_class:
            data = self.put_serializer_class().dump(saved_object)
            return ok_response(data)
        else:
            return ok_response({})


class PatchView(APIBaseView):
    """局部更新资源 view
    1. 获取上下文: 通过数据库或其他 model 层获取数据
    2. 验证请求数据
    3. 保存数据
    """

    args_deserializer_class = None
    patch_serializer_class = None

    def patch(self, *args, **kwargs):
        self.validated_data = self.get_validated_data(kwargs)

        # 保存数据
        patched_object = self.save()
        return self.response(patched_object)

    def get_validated_data(self, kwargs):
        # 反序列化请求数据
        if not self.args_deserializer_class:
            return {}

        request_data = self.parse_json()
        request_data.update(kwargs)
        deserializer = self.args_deserializer_class()
        validated_data = deserializer.load(request_data)
        return validated_data

    def save(self):
        """根据 self.validated_data 和 self.context 保存数据到数据库"""
        raise NotImplementedError

    def response(self, saved_object):
        """响应结果
        默认返回空 json 对象, 需要修改则在子类中覆盖这个方法
        """
        if self.patch_serializer_class:
            data = self.patch_serializer_class().dump(saved_object)
            return ok_response(data)
        else:
            return ok_response({})


class PostView(APIBaseView):
    """创建数据的 view"""

    args_deserializer_class = None
    post_serializer_class = None

    def post(self, *args, **kwargs):
        self.validated_data = self.get_validated_data(kwargs)

        # 保存数据
        saved_object = self.save()
        return self.response(saved_object)

    def get_validated_data(self, kwargs):
        # 反序列化请求数据
        if not self.args_deserializer_class:
            return {}

        request_data = self.parse_json()
        request_data.update(kwargs)
        deserializer = self.args_deserializer_class()
        validated_data = deserializer.load(request_data)
        return validated_data

    def save(self):
        """根据 self.validated_data 和 self.context 保存数据到数据库"""
        raise NotImplementedError

    def response(self, saved_object):
        """响应结果
        默认返回空 json 对象, 需要修改则在子类中覆盖这个方法
        """
        if self.post_serializer_class:
            data = self.post_serializer_class().dump(saved_object)
            return ok_response(data)
        else:
            return ok_response({})


class DeleteView(APIBaseView):
    """删除数据的 view
    1. 获取上下文: 通过数据库或其他 model 层获取数据
    2. 验证请求数据
    3. 保存数据
    """

    args_deserializer_class = None
    delete_serializer_class = None

    def delete(self, *args, **kwargs):
        self.validated_data = self.get_validated_data(kwargs)

        # 保存数据
        deleted_object = self.save()
        return self.response(deleted_object)

    def get_validated_data(self, kwargs):
        # 反序列化请求数据
        if not self.args_deserializer_class:
            return {}

        request_data = self.parse_json()
        request_data.update(kwargs)
        deserializer = self.args_deserializer_class()
        validated_data = deserializer.load(request_data)
        return validated_data

    def save(self):
        """
        具体执行操作, 由子类实现
        """
        raise NotImplementedError

    def response(self, deleted_object):
        """响应结果
        默认返回空 json 对象, 需要修改则在子类中覆盖这个方法
        """
        if self.delete_serializer_class:
            data = self.delete_serializer_class().dump(deleted_object)
            return ok_response(data)
        else:
            return ok_response({})


class ListView(APIBaseView):
    """List api view
    1. 反序列化传入的参数
    2. 获取一组数据
    3. 序列化一组数据
    """

    # 传入参数的的反序列化器
    args_deserializer_class = None
    # 过滤出来的结果的序列化器
    list_serializer_class = None
    list_result_name = "items"

    def get(self, *args, **kwargs):
        """处理 GET 请求"""
        self.validated_data = self.get_validated_data(kwargs)
        target_objects = self.filter_objects()
        return self.response(target_objects)

    def get_validated_data(self, kwargs):
        if not self.args_deserializer_class:
            return {}

        request_data = {}
        # 处理 GET 参数的格式，让 marshmallow 比较容易处理
        for key, value in request.args.items():
            if isinstance(value, list) and len(value) == 1:
                request_data[key] = value[0]
            else:
                request_data[key] = value

        request_data.update(kwargs)
        deserializer = self.args_deserializer_class()
        validated_data = deserializer.load(request_data)
        return validated_data

    def filter_objects(self):
        """获取需要序列化的对象"""
        raise NotImplementedError

    def response(self, results):
        """响应结果
        默认返回空 json 对象, 需要修改则在子类中覆盖这个方法
        """
        if not self.list_serializer_class:
            return ok_response({})

        _serializer = self.list_serializer_class()
        return ok_response({
            self.list_result_name: _serializer.dump(results, many=True),
        })


class MultiRetrievePutView(APIBaseView):
    args_deserializer_class = None
    multi_args_deserializer_class = None
    retrieve_serializer_class = None

    def put(self, *args, **kwargs):
        self.validated_data = self.get_validated_data(kwargs)
        retrieve_items = self.mget()

        serializer = self.retrieve_serializer_class()
        serialized_retrieve_items = [
            serializer.dump(item) for item in retrieve_items
        ]

        retrieve_items_with_allow_fields = self.filter_fields(
            serialized_retrieve_items
        )
        return ok_response({"items": retrieve_items_with_allow_fields})

    def get_validated_data(self, kwargs):
        # 反序列化请求数据
        request_data = self.parse_json()
        self.allow_fields = request_data.pop("fields", None)
        items = request_data.pop("items", None)
        if items is None:
            raise APIException(
                error_type="need_items_argument",
                error_message="mget api need items argument",
            )

        request_data.update(kwargs)
        if self.args_deserializer_class:
            args_deserializer = self.args_deserializer_class()
            result = args_deserializer.load(request_data)
        else:
            result = {}

        multi_args_deserializer = self.multi_args_deserializer_class()
        result.update({
            "items": [multi_args_deserializer.load(item) for item in items]
        })
        return result

    def mget(self):
        raise NotImplementedError

    def filter_fields(self, items):
        if self.allow_fields is None:
            return items

        results = []
        for item in items:
            # 只获取 item 中需要的字段
            _item = {}
            for field_name in self.allow_fields:
                # 确保 字段 一定存在于结果中
                if field_name not in item:
                    raise APIException(
                        error_type="field_not_in_item",
                        error_message=f"Field: {field_name} not in item",
                    )

                _item[field_name] = item[field_name]
            results.append(_item)

        return results


class AdminListView(GetView):
    """管理界面用的ListView"""

    def get(self, *args, **kwargs):
        """处理 GET 请求"""
        self.validated_data = self.get_validated_data(kwargs)
        target_object = self.get_object(kwargs)
        serialized_data = self.serialize(target_object)
        return ok_response(serialized_data)

    def get_context(self, kwargs):
        return {
            "start": int(request.args.get("start", 0)),
            "end": int(request.args.get("end", 10)),
            "order": request.args.get("order", "desc"),
            "sort": request.args.get("sort", "created_at"),
            "keyword": request.args.get("keyword", None),
            "size": int(request.args.get("size", 10)),
            "paging_state": request.args.get("paging_state", None),
        }

    def get_all_objects(self):
        raise NotImplementedError

    def search(self, results):
        raise NotImplementedError

    def paging_results(self, results, start, end, order_by, sort_field):
        if order_by.lower() == "desc":
            reverse = True
        else:
            reverse = False

        sorted_results = sorted(
            results, key=lambda x: getattr(x, sort_field), reverse=reverse
        )
        return sorted_results[start:end], len(sorted_results)

    def get_object(self, kwargs):
        self.context = self.get_context(kwargs)

        results = self.get_all_objects()
        results = self.search(results)

        paging_results, total_results = self.paging_results(
            results,
            self.context["start"],
            self.context["end"],
            self.context["order"],
            self.context["sort"],
        )
        self.context["total"] = total_results
        return paging_results

    def serialize(self, results):
        _serializer = self.get_serializer_class()
        return {
            "items": _serializer.dump(results, many=True),
            "total": self.context["total"],
        }


def deprecated_api(view):
    """
    为了保证客户端在第一时间会更新弃用的api，强制在staging服务器让api报错
    """

    @wraps(view)
    def decorator(*args, **kwargs):
        # 测试装饰器，项目中可删除 'debug', 'development', 'testing'
        if app.config["STAGE"] in (
            "debug", "development", "testing", "staging"
        ):
            return failed_response(
                error_type="api_deprecated",
                error_message="这个API已经标记为弃用, 请联系后端开发人员确认新的api",
            )

        if isinstance(view, MethodViewType):
            return view.as_view(view.__name__)()

        return view(*args, **kwargs)

    return decorator


def removed_api(view=None):
    """
    当标记了一断时间 deprecated 后，就可以标记成 remove_api
    这样客户端即使还没有升级，就会收到一个错误，提示需要升级
    """

    @wraps(view)
    def decorator(*args, **kwargs):
        # 测试装饰器，项目中可删除 'debug', 'development', 'testing'
        if app.config["STAGE"] in (
            "debug",
            "development",
            "testing",
            "staging",
            "production",
        ):
            return failed_response(
                error_type="api_removed",
                error_message="您的软件版本已过期了，请尽快升级。给您带来的不便，我们深表歉意",
            )

        if isinstance(view, MethodViewType):
            return view.as_view(view.__name__)()

        return view(*args, **kwargs)

    return decorator
