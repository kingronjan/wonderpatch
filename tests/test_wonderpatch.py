#!/usr/bin/env python

"""Tests for `wonderpatch` package."""

import os
import unittest
from unittest.mock import Mock

from wonderpatch import wonder


class TestObject(object):

    def name(self):
        return self.__class__.__name__

    @property
    def age(self):
        return 1

    def move(self, step, mm=1):
        print(f'{self} moved {step} to {mm}')


class TestWonderpatch(unittest.TestCase):
    """Tests for `wonderpatch` package."""

    def test_raise_error_when_not_called(self):
        with self.assertRaises(AssertionError):
            with wonder(TestObject.name).called_once(return_value=0):
                pass

    def test_raise_error_when_not_called_with(self):
        with self.assertRaises(AssertionError):
            with wonder(TestObject.move).called_once_with(1, mm=2):
                TestObject().move(1)

    def test_patch_method(self):
        with wonder(TestObject.name).called_once(return_value=0):
            assert TestObject().name() == 0

    def test_patch_property(self):
        with wonder(TestObject.age).called_once(return_value=111):
            assert TestObject().age == 111

    def test_module_method(self):
        with wonder(os).cpu_count.called_once(return_value=12345):
            assert os.cpu_count() == 12345

    def test_str_patch(self):
        with wonder('os.cpu_count').called_once(return_value=12345):
            assert os.cpu_count() == 12345

    def test_together_as_wrapper(self):
        @wonder.together
        def test():
            wonder(TestObject.name).called_once(return_value=0)
            wonder(TestObject.age).called_once(return_value=0)

            test_object = TestObject()
            assert test_object.age == 0
            assert test_object.name() == 0

        test()
        assert TestObject().name() == TestObject.__name__
        assert TestObject().age == 1

    def test_together_in_with_statement(self):

        with wonder.together():
            wonder(TestObject.name).called_once(return_value=0)
            wonder(TestObject.age).called_once(return_value=0)

            test_object = TestObject()
            assert test_object.age == 0
            assert test_object.name() == 0

        assert TestObject().name() == TestObject.__name__
        assert TestObject().age == 1

    def test_autospec_method(self):
        with wonder(TestObject.move), self.assertRaises(TypeError) as error:
            TestObject().move(1, 1, 2)
            assert 'too many positional arguments' in str(error)

    def test_mock_mock(self):
        m = Mock()

        with wonder(m.name).called_once(return_value=1):
            assert m.name() == 1

    def test_specify_new(self):
        m = Mock()
        m.return_value = 1

        with wonder(TestObject.move, new=m):
            assert TestObject.move() == 1
