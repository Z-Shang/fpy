from abc import ABCMeta, abstractmethod, abstractclassmethod


class Transparent(metaclass=ABCMeta):
    @abstractmethod
    def __underlying__(self):
        raise NotImplementedError

    def __getattr__(self, name):
        try:
            return self.__getattribute__(name)
        except AttributeError:
            return getattr(self.__underlying__(), name)
