'''
Copyright 2013 Dustin Frisch<fooker@lab.sh>

This file is part of require.

require is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

require is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with require. If not, see <http://www.gnu.org/licenses/>.
'''

import setuptools


setuptools.setup(
    license = 'GNU GPLv3',

    name = 'require',
    version = '0.1.1',

    author = 'Dustin Frisch',
    author_email = 'fooker@lab.sh',

    url = 'http://dev.open-desk.net/projects/require',

    description = 'A framework for module definitions',
    long_description = open('README').read(),
    keywords = 'require module',

    packages=['require'],

    install_requires = [
    ],

    
)
