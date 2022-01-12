import abc


class BaseMessage(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get(self):
        raise NotImplementedError
