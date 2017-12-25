# test_main.py - unit tests for rumbleinthejungle
#
# Copyright 2014, 2017 Jeffrey Finkelstein.
#
# This file is part of rumbleinthejungle.
#
# rumbleinthejungle is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# rumbleinthejungle is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# rumbleinthejungle.  If not, see <http://www.gnu.org/licenses/>.
"""Unit tests for :mod:`rumbleinthejungle`."""
import unittest

from rumbleinthejungle.__main__ import rhyming_pairs


class TestRhymingPairs(unittest.TestCase):

    def test_rhymes(self):
        actual = set(rhyming_pairs(['bickering'], ['pickering', 'flickering']))
        expected = {('bickering', 'pickering'), ('bickering', 'flickering')}
        self.assertEqual(actual, expected)