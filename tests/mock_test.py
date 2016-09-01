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

import unittest

from require.inject import *
from require.mock import *


class MockTestCase(unittest.TestCase):
    def test_mock(self):
        module = Module()

        @module.export(name='export',
                       scope=singleton)
        def exported():
            class Export(object):
                def get(me):
                    return "test"
            return Export()

        @mock(module, 'export')
        def mock_export(export):
            export.get.return_value = "mocked"

        @mock_export
        @module.inject(export='export')
        def tester(export):
            self.assertEqual(export.get(), "mocked")

        tester()
