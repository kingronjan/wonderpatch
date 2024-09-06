===========
wonderpatch
===========


.. image:: https://img.shields.io/pypi/v/wonderpatch.svg
        :target: https://pypi.python.org/pypi/wonderpatch


Better patch for test.


Usage
------

patch module method
^^^^^^^^^^^^^^^^^^^

.. code:: python

    import sys

    from wonderpatch import wonder

    with wonder(os).cpu_count.called_once(return_value=12345):
        assert os.cpu_count() == 12345


Use path is ok:

.. code:: python

    import sys

    from wonderpatch import wonder

    with wonder('os.cpu_count').called_once(return_value=12345):
        assert os.cpu_count() == 12345


patch object
^^^^^^^^^^^^

.. code:: python

    from wonderpatch import wonder

    class TestObject:

        def name(self):
            return self.__class__.__name__


    with wonder(TestObject.name).called_once(return_value='x'):
        assert TestObject().name() == 'x'


It is also works for property:

.. code:: python

    from wonderpatch import wonder

    class TestObject:

        @property
        def name(self):
            return self.__class__.__name__


    with wonder(TestObject.name).called_once(return_value='x'):
        assert TestObject().name == 'x'


Multiple patch in one function
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to use multiple patches in one place, and do not want to write a verify long statement, use `wonder.together`:

.. code:: python

    from wonderpatch import wonder

    with wonder.together():
        wonder(TestObject.name).called_once(return_value='x')
        wonder(TestObject.age).called_once(return_value='x')

        assert TestObject().name() == 'x'
        assert TestObject().age == 'x'


Or as a decorator:

.. code:: python

    from wonderpatch import wonder

    @wonder.together
    def test_name():
        wonder(TestObject.name).called_once(return_value='x')
        assert TestObject().name() == 'x'


the wonder api
^^^^^^^^^^^^^^

- wonder(...).then_return(value: Any)

  patch and set return value, works for called 0+ times

- wonder(...).then_raise(exception)

  patch and set raise value, works for called 0+ times

- wonder(...).called(*times=None, min=1, max=None, return_value=_empty, side_effect=_empty, only_self=False*)

  patch and set min or max times call, default is at least 1 time.

- wonder(...).called_with(`*args, **kwargs`)

  patch and set called at least once with `args, kwargs`

- wonder(...).called_once_with(`*args, **kwargs`)

  patch and set called once with `args, kwargs`

- wonder(...).never_called()

  patch and set never called.




Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
