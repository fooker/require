"""
Copyright 2016 Dustin Frisch<fooker@lab.sh>

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

import functools


__all__ = ['Module',
           'oneshot',
           'singleton']



class Export(object):
    def __init__(self,
                 factory,
                 name,
                 scope):
        self.__factory = factory
        self.__name = name
        self.__scope = scope

        self.__extenders = []

        # The getter is used to return the scoped instance - late binding the
        # create function via lambda as mocking may overwrite it after
        # construction
        self.__getter = scope(lambda: self.create())


    def extend(self, extender):
        """ Extends this export.

            The instance created by the wrapped factory is extended by passing the
            created instance to the given extender function after creation.

            The extend function must accept the instance as its only argument. If
            the function returns a value which is not None, the instance is replaced
            with the returned value.
        """

        self.__extenders.append(extender)


    def __call__(self):
        """ Returns the instance.

            The created instance is scoped by the specified scoping function.
        """

        return self.__getter()


    def create(self):
        """ Creates a new instance.

            The instance is created by calling the exported factory and
            applying all extenders in the order of registration.

            This would always create a new instance regardless of the scope of
            this export. Just call the export to get a scoped instance.
        """

        # Create the instance by calling the factory
        instance = self.__factory()

        # Call all extenders for this export to update or replace the instance
        for extender in self.__extenders:
            # If the extender is an export, get a concrete instance
            if isinstance(extender, Export):
                extender = extender()

            extended = extender(instance)

            # If the extender returned a not-none value, the instance is
            # replaced with the returned value
            if extended is not None:
                instance = extended

        return instance


    @property
    def factory(self):
        return self.__factory


    @property
    def name(self):
        return self.__name


    @property
    def scope(self):
        return self.__scope



class InjectProperty(object):
    """ Property descriptor used to inject single requirements as class
        properties.

        Injected properties should be created via the Module.inject method.
    """

    def __init__(self,
                 export):
        self.__export = export


    def __get__(self, instance, owner):
        if instance is None:
            # Return the plain export on static access
            return self.__export

        else:
            # Return the value from the export on instance access
            return self.__export()



def oneshot(factory):
    """ Scope 'oneshot'.

        The scope does not apply any caching or reusing of exported objects.
        Each request for en export wil recreate the exported object.
    """

    # Always create and return the instance as-is
    return factory



def singleton(factory):
    """ Scope 'singleton'.

        The singleton scope ensures, that only one single instance exists
        during application life-time. The instance is created on first request
        and cached for later use.
    """

    instance = None

    def wrapper():
        # Ensure the instance exists
        nonlocal instance
        if instance is None:
            instance = factory()

        return instance

    return wrapper



class Module(object):
    def __init__(self):
        self.__exports = {}


    def load(self, requirement):
        """ Load a requirement and return the export to fulfill the
            requirement.
        """

        if requirement not in self.__exports:
            raise KeyError("Unknown requirement: " + requirement)

        return self.__exports[requirement]


    def wrap(self, func, **requirements):
        """ Wraps a function for injecting requirements.
        """

        # Load all exports as specified in the requirements
        exports = {name: self.load(requirement)
                   for name, requirement
                   in requirements.items()}


        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            # Extend the keyword arguments with the required instances for all
            # missing arguments
            # TODO: Add more magic to allow positional overrides
            for name, export in exports.items():
                if name not in kwargs:
                    kwargs[name] = export()

            # Call the wrapped function
            return func(*args, **kwargs)


        return wrapped


    def export(self,
               name=Ellipsis,
               scope=singleton,
               **requirements):
        """ Decorator to export a factory.

            Requirements for the factory can be specified. These requirements
            are passed to the wrapped function as specified by the
            Module.inject decorator.

            If the name is not specified, the module name and the factory name
            separated by colon is used.
        """

        def exporter(factory):
            if requirements:
                factory = self.wrap(factory, **requirements)

            # Ensure the export has a name
            nonlocal name
            if name is Ellipsis:
                name = '%s:%s' % (factory.__module__, factory.__name__)

            # Avoid overwriting exports
            if name in self.__exports:
                raise KeyError("Export already exists: " + name)

            # Create export instance and remember it for injection lookup
            export = self.__exports[name] = Export(factory=factory,
                                                   name=name,
                                                   scope=scope)

            # Attach the export to the factory for extension lookup
            setattr(factory, '__export__', export)

            # Return the original function
            return factory

        return exporter


    def extend(self,
               requirement,
               **requirements):
        """ Decorator to extend a export.

            The decorated function is used to extend the export specified by
            the given name.

            Requirements for the factory can be specified. These requirements
            are passed to the wrapped function as specified by the `require`
            decorator.
        """
        def wrapper(extender):
            self.load(requirement).extend(self.wrap(extender, **requirements))

        return wrapper


    def inject(self,
               requirement=None,
               **requirements):
        """ Factory for a function decorator or property descriptor.
            Decorator to inject requirements into a function.

            If a single unnamed requirement is passed, a property will be
            created which returns the required instance on access.

            A decorated function is returned if keyword parameters are passed.
            The decorated function is wrapped in a way that keyword arguments
            can be omitted if an according requirement was specified. All
            skipped arguments will be filled by the required instances.
        """

        # Ensure only one call style is used
        assert (requirement is None) != (len(requirements) == 0)

        if requirement:
            # Load the export specified in the requirement and build a property accessor for the injection
            return InjectProperty(self.load(requirement))

        elif requirements:
            # Return the wrapper function
            def wrapper(func):
                return self.wrap(func, **requirements)

            return wrapper
