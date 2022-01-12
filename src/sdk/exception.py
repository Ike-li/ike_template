"""
请不要将业务逻辑加入这个文件中
"""


class SDKException(Exception):
    """内部调用的异常"""

    def __init__(
        self,
        error_type="service_call_error",
        error_message="Error occurred during service api call",
    ):
        self.error_type = error_type
        self.error_message = error_message

    def __repr__(self):
        return "<{} {}: {}>".format(
            self.__class__, self.error_type, self.error_message
        )
