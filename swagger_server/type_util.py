# coding: utf-8

import sys

if sys.version_info < (3, 7):
    import typing

    def is_generic(klass):
        """Determine whether klass is a generic class (до Python 3.7)"""
        return type(klass) is typing.GenericMeta

    def is_dict(klass):
        """Determine whether klass is a Dict (до Python 3.7)"""
        return getattr(klass, '__extra__', None) == dict

    def is_list(klass):
        """Determine whether klass is a List (до Python 3.7)"""
        return getattr(klass, '__extra__', None) == list

else:

    def is_generic(klass):
        """Determine whether klass is a generic class (Python 3.7+)"""
        return hasattr(klass, '__origin__')

    def is_dict(klass):
        """Determine whether klass is a Dict (Python 3.7+)"""
        return getattr(klass, '__origin__', None) == dict

    def is_list(klass):
        """Determine whether klass is a List (Python 3.7+)"""
        return getattr(klass, '__origin__', None) == list
