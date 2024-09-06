#!/usr/bin/env python

"""Tests for `wonderpatch` package."""

import os
import unittest

from wonderpatch import wonder


class TestObject(object):

    def name(self):
        return self.__class__.__name__

    @property
    def age(self):
        return 1


class TestWonderpatch(unittest.TestCase):
    """Tests for `wonderpatch` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

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
