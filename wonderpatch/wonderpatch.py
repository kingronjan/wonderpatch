import importlib
import inspect
import logging
from contextlib import ContextDecorator
from unittest.mock import ANY, MagicMock, Mock, PropertyMock, call, patch

_empty = object()

logger = logging.getLogger(__name__)


def wonder_patch(target, item, new):
    if item is None:
        path = target
        raw = None
    else:
        path = getattr(target, '__name__', str(target)) + '.' + item
        raw = getattr(target, item)

    if new is _empty:
        if isinstance(raw, property):
            new = PropertyMock()
        else:
            new = MagicMock()

    if hasattr(raw, '__name__'):
        new.__name__ = raw.__name__

    if inspect.ismodule(target) or isinstance(target, str):
        p = patch(path, new=new)
        p.start()

    else:
        p = patch.object(target, item, new=new)
        p.start()

        if not inspect.ismethod(raw) and not inspect.isfunction(raw):
            setattr(target, item, new)

    return path, p, new


class Patch(object):
    def __init__(self, target, new=_empty, patch=None, path=None, min_times=None, max_times=None, times=None,
                 only_self=False):
        self.mock = new
        self.patch = patch
        self.target = target
        self.path = path
        self.times = times
        self.call = None
        self.side_effect = None
        self.min_times = min_times
        self.max_times = max_times
        self.only_self = only_self
        self.validated = False

        if self.times is not None:
            self.call = ANY

    def __getattr__(self, item):
        if object.__getattribute__(self, 'patch') is not None:
            raise RuntimeError('already patched: %s' % self)

        self.path, self.patch, self.mock = wonder_patch(self.target, item, self.mock)
        return self

    def __call__(self, *args, **kwargs):
        if kwargs or len(args) != 1:
            self.call = call(*args, **kwargs)
            return self

        arg = args[0]
        if arg is Ellipsis or arg is ANY:
            self.call = ANY

        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_and_validate()

    def __str__(self):
        return "<WonderPatch('%s')>" % self.path

    def then_return(self, value):
        """set return value, works for call 0+ times."""
        self.mock.return_value = value
        return self

    def then_raise(self, exception):
        self.mock.side_effect = exception
        return self

    def then_call(self, fn):
        """set mock side effect"""
        self.mock.side_effect = fn
        return self

    def stop_and_validate(self):
        """stop patch and validate"""
        if self.patch is None:
            return

        self.stop()
        self.validate()

    def stop(self):
        """stop patch"""
        if self.patch is None:
            return

        try:
            self.patch.stop()
        except RuntimeError:
            pass

    def validate(self):
        """validate set calls and arguments."""
        if self.patch is None:
            return

        if self.validated:
            return

        if all(x is None for x in [self.times, self.min_times, self.max_times]):
            return

        if not isinstance(self.mock, Mock):
            raise ValueError('not support validate for %s' % self.mock)

        matched_calls = [c for c in self.mock.mock_calls if c == self.call]
        if self.only_self:
            matched_calls = [c for c in matched_calls if not c[0]]

        def error_message(times):
            return 'expect %s called with %s %s times, actual: %s' % (self.path, self.call, times, len(matched_calls))

        if self.times is not None:
            assert len(matched_calls) == self.times, error_message(self.times)

        if self.min_times is not None:
            assert len(matched_calls) >= self.min_times, error_message('at least %s' % self.min_times)

        if self.max_times is not None:
            assert len(matched_calls) <= self.max_times, error_message('at the most %s' % self.max_times)

        logger.debug('%s validated' % self)
        self.validated = True

    def called(self, times=None, min=1, max=None, return_value=_empty, side_effect=_empty, only_self=False):
        """
        :param times: want called exactly times.
        :param min: want called at least times.
        :param max: want called at most times.
        :param return_value: want return value.
        :param side_effect: want side_effect, more usage see:
          `unittest.mock <https://docs.python.org/zh-cn/3/library/unittest.mock.html#unittest.mock.Mock.side_effect>`_.
        :param only_self: want only self calls,
            for example, `x()` is self calls, `x.xx()` is not.
        """
        if times is not None:
            min = None

        self.call = ANY
        self.times = times
        self.min_times = min
        self.max_times = max
        self.only_self = only_self

        if return_value is not _empty:
            return self.then_return(return_value)

        if side_effect is not _empty:
            return self.then_call(side_effect)

        return self

    def called_once_with(self, *args, **kwargs):
        """wonder called exactly once with give arguments."""
        self.call = call(*args, **kwargs)
        self.times = 1
        return self

    def called_with(self, *args, **kwargs):
        """wonder called at least once with give arguments."""
        self.call = call(*args, **kwargs)
        self.min_times = 1
        return self

    def called_once(self, return_value=_empty, **kwargs):
        """shortcut for wonder.called(1, **kwargs)"""
        return self.called(1, return_value=return_value, **kwargs)

    def never_called(self):
        """wonder never called."""
        return self.called(0)


class Wonder(object):
    def __init__(self):
        self.wondering = False
        self.patches = []

    def __call__(self, target, new=_empty, times=None, min_times=None, max_times=None, is_property=False):
        """
         :param target: cloud be str, method, function, property.
         :param new: set mock object, default is PropertyMock for property object, MagicMock for else.
         :param times: want called exactly times.
         :param min_times: want called at least times.
         :param max_times: want called at most times.
         :param is_property: if True, the mock object will use PropertyMock replace MagicMock
         """
        if isinstance(target, property):
            target = target.fget

        if inspect.ismethod(target):
            item = target.__name__
            path, patch, new = wonder_patch(target.__self__, item, new)

        elif isinstance(target, Mock):
            attrs = vars(target)
            item = attrs['_mock_new_name']
            path, patch, new = wonder_patch(attrs['_mock_new_parent'], item, new)

        elif inspect.isfunction(target) or inspect.isbuiltin(target):
            item = target.__qualname__
            module = target.__module__

            if '.' in item:
                cls, item = item.split('.', maxsplit=1)
                obj = importlib.import_module(module)
                target = getattr(obj, cls)
            else:
                target = importlib.import_module(module)

            path, patch, new = wonder_patch(target, item, new)

        elif isinstance(target, str):
            path, patch, new = wonder_patch(target, None, new)

        else:
            path, patch = None, None
            if is_property:
                new = PropertyMock()

        p = Patch(target, new, path=path, patch=patch, min_times=min_times, max_times=max_times, times=times)

        if self.wondering:
            self.patches.append(p)

        return p

    def together(self, fn=None):
        """
        use multiple wonder in one place, can use as decorator or with statement.

        ex:
            . code:: python

                with wonder.together():
                    wonder(TestObject.name).called_once(return_value='x')
                    wonder(TestObject.age).called_once(return_value='x')

                    ...

            or as decorator:
            . code:: python

                @wonder.together
                def test_fn():
                    ...

        """
        if callable(fn):
            return Together(self)(fn)
        return Together(self)

    def validate(self, stop=True):
        if stop:
            for p in self.patches:
                p.stop()

        try:
            for p in self.patches:
                p.validate()

        finally:
            if stop:
                self.stop_wondering()

    def start_wondering(self):
        self.wondering = True
        self.patches = []

    def stop_wondering(self):
        self.wondering = False
        self.patches = []


class Together(ContextDecorator):

    def __init__(self, wonder):
        self.wonder = wonder

    def __enter__(self):
        if not self.wonder.wondering:
            self.wonder.start_wondering()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.wonder.validate(stop=True)


wonder = Wonder()
