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

import unittest

from require.inject import *



class InjectTestCase(unittest.TestCase):
    def test_export(self):
        module = Module()

        @module.export(scope=oneshot)
        def exported():
            pass

        export = module.load('tests.inject_test:exported')

        self.assertEqual(export.name, 'tests.inject_test:exported')
        self.assertEqual(export.scope, oneshot)
        self.assertEqual(export.factory, exported)


    def test_simple_create(self):
        module = Module()

        @module.export(name='export')
        def exported():
            return "test"

        export = module.load('export')

        self.assertEqual(export(), "test")


    def test_extended_create(self):
        module = Module()

        @module.export(name='export')
        def exported():
            return 'test'

        @module.extend('export')
        def extend(exported):
            return exported + '!'


        export = module.load('export')

        self.assertEqual(export(), 'test!')


    def test_scoping(self):
        module = Module()

        @module.export(name='singleton',
                       scope=singleton)
        def exported():
            return object()

        @module.export(name='oneshot',
                       scope=oneshot)
        def exported():
            return object()

        singleton_export = module.load('singleton')
        self.assertEqual(singleton_export(), singleton_export())

        oneshot_export = module.load('oneshot')
        self.assertNotEqual(oneshot_export(), oneshot_export())


    def test_method_injection(self):
        module = Module()

        @module.export(name='exported')
        def exported():
            return 'test'

        @module.inject(exported='exported')
        def tester(exported):
            self.assertEqual(exported, 'test')

        tester()


    def test_method_injection_overwrite(self):
        module = Module()

        @module.export(name='exported')
        def exported():
            return 'test'

        @module.inject(exported='exported')
        def tester(exported):
            self.assertEqual(exported, 'override')

        tester(exported='override')


    def test_property_injection(self):
        module = Module()

        @module.export(name='exported')
        def exported():
            return 'test'

        class Tester(object):
            exported = module.inject('exported')

            def __call__(me):
                self.assertEqual(me.exported, 'test')

        tester = Tester()
        tester()


    def test_property_injection_static(self):
        module = Module()

        @module.export(name='exported')
        def exported():
            return 'test'

        class Tester(object):
            exported = module.inject('exported')

        self.assertEqual(Tester.exported.name, 'exported')
