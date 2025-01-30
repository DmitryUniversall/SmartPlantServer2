from abc import ABCMeta

from src.core.utils.singleton import SingletonMeta


class BaseResourceSTMeta(ABCMeta, SingletonMeta):
    pass
