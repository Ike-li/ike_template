from flask_babel import lazy_gettext as _


class APIException(Exception):
    """api 异常"""

    error_type = "api_error"
    error_message = "A server error occurred."

    def __init__(self, error_type=None, error_message=None):
        if error_type is not None:
            self.error_type = error_type
        if error_message is not None:
            self.error_message = error_message

    def __repr__(self):
        return "<{} {}: {}>".format(
            self.__class__, self.error_type, self.error_message
        )


class PermissionDenied(APIException):
    error_type = "permission_denied"
    error_message = _("Permission denied")


class ObjectNotFound(APIException):
    error_type = "object_not_found"
    error_message = _("Object not found")


# 注意：请不要在这个文件中添加业务逻辑的异常
