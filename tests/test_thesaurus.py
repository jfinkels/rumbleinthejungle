# test_thesaurus.py - unit tests for the thesaurus
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
"""Unit tests for the thesaurus classes."""
import unittest

from rumbleinthejungle.__main__ import THESAURUS_INDEX
from rumbleinthejungle.__main__ import THESAURUS_DATA
from rumbleinthejungle.thesaurus import Thesaurus
from rumbleinthejungle.thesaurus import ThesaurusIndex


class TestThesaurusIndex(unittest.TestCase):

    def test_byte_offset(self):
        """Tests that the index correctly computes the byte offset from the file.

        """
        with ThesaurusIndex(THESAURUS_INDEX) as index:
            assert index.byte_offset('simple') == 15076188
            assert index.byte_offset('travesty') == 17018737
            assert index.byte_offset('banana') == 1314743



class TestThesaurus(unittest.TestCase):

    def test_synonyms(self):
        """Tests that the thesaurus correctly provides synonyms to a given word."""
        with ThesaurusIndex(THESAURUS_INDEX) as index, \
                Thesaurus(THESAURUS_DATA, index) as thesaurus:
            # These are taken from the example given in the original documentation
            # for the thesaurus data file.
            assert thesaurus.synonyms('junk') == \
                {'debris', 'dust', 'rubble', 'detritus', 'rubbish', 'trash',
                 'scrap', 'boat', 'trash', 'scrap', 'discard', 'fling', 'toss',
                 'toss out', 'toss away', 'chuck out', 'cast aside', 'dispose',
                 'throw out', 'cast out', 'throw away', 'cast away', 'put away'}
