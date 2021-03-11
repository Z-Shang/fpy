from abc import ABCMeta, abstractmethod, abstractclassmethod


class Composable(metaclass=ABCMeta):
    @abstractmethod
    def __compose__(self, other):
        raise NotImplementedError

    def __xor__(self, other):
        return self.__compose__(other)
