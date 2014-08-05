"""
Copyright 2013 Dustin Frisch<fooker@lab.sh>

This file is part of require.

require is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

require is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with require.  If not, see <http://www.gnu.org/licenses/>.
"""

__all__ = ['require',
           'export',
           'extend']


class Export(object):
    """ Wrapper for an exported factory.

        The wrapper manages the instance creation using the wrapped factory by
        calling the factory on the first requirement. The created instance is
        stored in a singleton manner and returned on further requirements.

        The export also manages the registered extends for the factory. These
        extends are called after instance creation to manipulate the instance.
    """

    def __init__(self, factory):
        self.__factory = factory
        self.__extenders = []

        self.__instance = None

    def extend(self, extender):
        """ Extends this export.

            The instance created by the wrapped factory is extended by passing the
            created instance to the given extender function after creation.

            The extend function must accept the instance as its only argument. If
            the function returns a value which is not None, the instance is replaced
            with the returned value.
        """

        assert self.__instance is None

        self.__extenders.append(extender)

    @property
    def instance(self):
        """ Returns the instance.

            If no instance exists, it is created as described above.
        """

        # Create an instance none is available
        if self.__instance is None:

            # Lazily create the instance by calling the factory
            instance = self.__factory()

            # Call all extenders for this export to update or replace the instance
            for extender in self.__extenders:
                extended = extender(instance)

                # If the extender returned a not-none value, the instance is
                # replaced with the returned value
                if extended is not None:
                    instance = extended

            # Remember the instance for further requisition
            self.__instance = instance

        return self.__instance

    @staticmethod
    def load(requirement):
        """ Loads an export by the given name.

            The name must be a full specified identifier where the module name and
            the factory name are separated by a colon. The module containing the
            export is imported using the current context and the export is retrieved
            from the module.
        """

        module, export = requirement.split(':', 1)

        # Import the module containing the export
        module = __import__(name = module,
                            globals = globals(),
                            locals = locals(),
                            fromlist = [export],
                            level = 0)

        # Get the export from the imported module
        export = getattr(module, export)

        # Check if the given name refers a exported factory
        if not isinstance(export, Export):
            raise TypeError('%s is not exported' % requirement)

        return export


def require(**requirements):
    """ Decorator to inject requirements into a function.

        The decorated function is called with a named argument for each
        specified requirement containing the exported instances.
    """

    exports = {name: Export.load(requirement)
               for name, requirement
               in requirements.iteritems()}

    def wrapper(func):
        def wrapped(*args, **kwargs):
            # Populate the keyword arguments dicts passed to the wrapped
            # function with the required instances
            kwargs.update({name: export.instance
                           for name, export
                           in exports.iteritems()
                           if name not in kwargs})

            # Call the wrapped function
            return func(*args,
                        **kwargs)

        # Copy properties from the wrapped function to the wrapper
        wrapped.__module__ = func.__module__
        wrapped.__name__ = func.__name__
        wrapped.__qualname__ = func.__qualname__
        wrapped.__doc__ = func.__doc__

        return wrapped
    return wrapper


def export(**requirements):
    """ Decorator to export a factory.

        Requirements for the factory can be specified. These requirements are
        passed to the wrapped function as specified by the `require` decorator.
    """

    def wrapper(func):
        return Export(factory = require(**requirements)(func))

    return wrapper


def extend(requirement):
    """ Decorator to extend a export.

        The decorated function is used to extend the export specified by the given
        name.
    """

    def wrapper(func):
        Export.load(requirement).extend(extender = func)

    return wrapper
