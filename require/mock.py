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

import unittest.mock
import functools


__all__ = ['mock']



def mock(module, requirement):
    """ Mocks an export.

        The export specified by the passed requirement is patched to create a
        unittest.mock.Mock instance instead of the using the original factory.

        The Mock instance is passed to the decorated function as its only
        parameter for further modification every time an instance is created.
        This function can modify the mock in any way.

        The decorated function acts as a decorator itself. Each function
        decorated with it will use the patched version of the export instead of
        the real one.
    """

    # Find the export to mock
    export = module.load(requirement)

    def wrapper(mocker):
        @functools.wraps(mocker)
        def mocking(func):
            @functools.wraps(func)
            def wrapped(*args, **kwargs):
                # Mock the exports factory function
                with unittest.mock.patch.object(export, 'create',
                                                unittest.mock.Mock(name='mocked:%s' % requirement)) as mocked:
                    # Modify the mocked factory function
                    mocker(mocked())

                    # Call the wrapped function with the patch in place
                    return func(*args, **kwargs)

            return wrapped
        return mocking
    return wrapper
