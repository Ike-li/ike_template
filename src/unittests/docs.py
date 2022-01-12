import json
import os
from pathlib import Path

import decorator
import pytest
from flask.testing import FlaskClient


class Api:
    title = None
    path = None
    method = None
    headers = {}
    params = {}
    body = {}
    responses = {}

    def __init__(
        self,
        title,
        path,
        method,
        headers,
        params,
        body,
        responses,
        customized_response=None,
    ):
        self.title = title
        self.path = path
        self.method = method
        if headers:
            self.headers = headers
        if params:
            self.params = params
        if body:
            self.body = body
        self.responses = responses
        self.customized_response = customized_response


class DocsGenerator:
    """用于在跑测试时 创建生成 API 文档

    docs = Docs()
    docs.add_api_docs(...)
    docs.add_api_docs(...)
    docs.build()
    """

    apis = dict()

    def add_api_docs(
        self,
        title,
        path,
        method,
        headers,
        params,
        body,
        responses,
        customized_response,
        file=None,
    ):
        if file is None:
            file = "readme.md"
        if file not in self.apis:
            self.apis[file] = list()
        self.apis[file].append(
            Api(
                title,
                path,
                method,
                headers,
                params,
                body,
                responses,
                customized_response,
            )
        )

    def build_docs(self):
        # 生成目录
        toc = ""
        for filename in self.apis:
            toc += f"[{filename}]({filename})\n"

        docs_dir = Path(Path(__file__).parent.parent.parent, "docs")
        if not docs_dir.exists():
            os.makedirs(docs_dir)

        for filename in self.apis:
            doc_file_path = Path(docs_dir, filename)

            if not Path(os.path.dirname(doc_file_path)).exists():
                os.makedirs(os.path.dirname(doc_file_path))

            _doc_file = open(doc_file_path, "w+", encoding="utf-8")
            _doc_file.write(toc)
            for index, api in enumerate(self.apis[filename]):
                self._build(api, _doc_file, index)
            _doc_file.close()
            print("Doc file update:", os.path.abspath(doc_file_path))

    def _build_request(self, api, f):
        """请求字段描述"""
        f.write("**请求**: \n\n")
        f.write("| 方法名 | 参数 | 描述 |\n| --- | --- | --- |\n")
        f.write(f"| path | `{api.path}` | - |\n")
        f.write(f"| method | `{api.method}` | - |\n")

        for key, value in api.headers.items():
            if value:
                f.write(f"| header | `{key}` | {value} |\n")
        for key, value in api.params.items():
            if value:
                f.write(f"| params | `{key}` | {value} |\n")
        for key, value in api.body.items():
            if value:
                f.write(f"| body | `{key}` | {value} |\n")
        f.write("\n")

    def _build_customized_response(self, api, f):
        """自定义响应字段描述"""
        if api.customized_response:
            f.write("部分响应字段描述: \n")
            f.write("| 字段名 | 描述 |\n| --- | --- |\n")
            for key, value in api.customized_response.items():
                if value:
                    f.write(f"| `{key}` | {value} |\n")
            f.write("\n")

    def _build_responses(self, api, doc_file):
        if api.responses is None:
            raise ValueError(
                f"API ({api.title}) should return "
                f"a response object."
            )

        for description, response in api.responses.items():
            _response = json.dumps(
                response, indent=2, ensure_ascii=False, sort_keys=True
            )
            response = f"{description}: \n```json\n{_response}\n```\n"
            doc_file.write(response)

    def _build(self, api, doc_file, index):
        title = f"\n## {index} {api.title}\n"
        doc_file.write(title)
        self._build_request(api, doc_file)
        self._build_customized_response(api, doc_file)
        self._build_responses(api, doc_file)


@pytest.mark.docs
def api_docs(
    title,
    path,
    method,
    headers=None,
    params=None,
    body=None,
    customized_response=None,
    file=None,
):
    """装饰器, 在测试函数上使用, 生成文档
    example:

    @api_docs(title='请求获取好友列表', path='/v1/friend/', method='GET',
              body=None)
    def test_list_friends(client):
        ...
        return {'正确响应': json_result}
    """

    def wrapper(func):

        def inner(_func, *args, **kwargs):
            """获取测试运行结果作为 http response 添加到文档中"""
            responses = _func(*args, **kwargs)

            client = None
            for arg in args:
                if isinstance(arg, FlaskClient):
                    client = arg
                    break
            if client is None:
                raise Exception("Test client not found")

            client.docs_generator.add_api_docs(
                title=title,
                path=path,
                method=method,
                headers=headers,
                params=params,
                body=body,
                responses=responses,
                customized_response=customized_response,
                file=file,
            )
            return responses

        return decorator.decorator(inner, func)

    return wrapper
