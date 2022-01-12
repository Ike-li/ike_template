"""
基础模块
"""
from re import finditer


class EngineException(Exception):
    error_message = "model base exception"

    def _camel_case_split(self, identifier):
        matches = finditer(
            ".+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)", identifier
        )
        return [_match.group(0).lower() for _match in matches]

    @property
    def error_type(self):
        return "_".join(self._camel_case_split(self.__class__.__name__))
