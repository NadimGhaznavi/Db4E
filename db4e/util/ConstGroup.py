"""
db4e/Modules/ContGroup.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""


class MetaConst(type):
    """
    Metaclass that collects public attributes into a dictionary-like mapping.
    """

    def __new__(mcs, name, bases, namespace):
        """
        Create the class and build the constants mapping.

        :param mcs: Metaclass reference.
        :type mcs: type
        :param name: Class name being created.
        :type name: str
        :param bases: Base classes for the new class.
        :type bases: tuple
        :param namespace: Class namespace dictionary.
        :type namespace: dict
        :return: Newly created class.
        :rtype: type
        """
        cls = super().__new__(mcs, name, bases, namespace)
        cls._constants = {
            k: v for k, v in namespace.items()
            if not k.startswith("_") and not callable(v)
        }
        return cls

    def __getitem__(cls, key):
        """
        Return a constant value by key.

        :param key: Constant name.
        :type key: str
        :return: Constant value.
        :rtype: object
        """
        return cls._constants[key]

    def keys(cls):
        """
        Return the constant keys.

        :return: Constant keys.
        :rtype: dict_keys
        """
        return cls._constants.keys()

    def values(cls):
        """
        Return the constant values.

        :return: Constant values.
        :rtype: dict_values
        """
        return cls._constants.values()

    def items(cls):
        """
        Return the constant items.

        :return: Constant items.
        :rtype: dict_items
        """
        return cls._constants.items()

    def __iter__(cls):
        """
        Return an iterator over constant keys.

        :return: Iterator over constant keys.
        :rtype: iterator
        """
        return iter(cls._constants)

    def __contains__(cls, item):
        """
        Check if a constant key exists.

        :param item: Constant key to check.
        :type item: str
        :return: True if key exists.
        :rtype: bool
        """
        return item in cls._constants

    def __repr__(cls):
        """
        Return a representation of the constant group.

        :return: String representation.
        :rtype: str
        """
        return f"<ConstGroup {cls.__name__}: {cls._constants!r}>"


class ConstGroup(metaclass=MetaConst):
    """
    Base class for constant groups (dict + namespace).
    """

    pass
