# thesaurus.py - thesaurus classes
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
"""Classes and functions for finding synonyms."""
import logging

__all__ = (
    'all_synonyms',
    'Thesaurus',
    'ThesaurusIndex',
)

#: A set of all parts of speech known to the thesaurus.
ALL_PARTS_OF_SPEECH = frozenset({'adj', 'noun', 'verb', 'adv'})


class ThesaurusIndex:
    """Represents an index indicating the location of each word in the
    thesaurus.

    The index data is stored in a file with the following format.  The first
    line indicates the encoding of the file. The second line indicates the
    number of entries in the index. Each subsequent line is an entry in the
    index. It consists of a thesaurus entry and a byte offset, separated by a
    pipe character ("|"). The byte offset indicates the location of the
    corresponding thesaurus entry in the thesaurus file so that it can be found
    by a single call to :func:`seek`.

    `filename` is the location of the thesaurus index file.

    This class should be used as a context manager, as follows::

        with ThesaurusIndex('myindex.txt') as index, \
                Thesaurus('mythesaurus.txt', index) as thesaurus:
            print(thesaurus.synonyms('cool'))

    """
    def __init__(self, filename):
        self.filename = filename

    def __enter__(self):
        self.offsets = {}
        self.fd = open(self.filename)
        encoding = self.fd.readline()
        logging.debug('Ignoring encoding %s', encoding)
        # TODO we could use this for a binary search instead but it would be
        # even *more* complicated.
        number_of_entries = self.fd.readline()
        logging.debug('Ignoring number of entries %s', number_of_entries)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fd.close()
        # this means do not suppress exceptions raised within the context
        return False

    def byte_offset(self, target):
        """Returns the location, in number of bytes, of the specified thesaurus
        entry in the thesaurus file.

        `target` is an entry in the thesaurus file.

        """
        # Check if the target has already been read on a previous call to this
        # method.
        if target in self.offsets:
            return self.offsets[target]
        # Read one line at a time, looking for the target, and reading
        line = self.fd.readline()
        while line is not None:
            entry, offset = line.split('|')
            # Record the byte offset for this entry.
            self.offsets[entry] = int(offset)
            # If we have passed the target, we know it doesn't exist in the
            # list further down, since the index is in lexicographic order, so
            # we can immediately break from the loop (and hence return -1).
            if entry > target:
                break
            # If we found a match, immediately return the offset
            if entry == target:
                return int(offset)
            # Otherwise, continue the search.
            line = self.fd.readline()
        # Otherwise, we have reached the end of the file somehow without
        # finding the entry but also without having returned -1, so we'll
        # return -1 here just to be safe.
        return -1


class Thesaurus:
    """A thesaurus backed by a file.

    `filename` is the location of the thesaurus file.

    `index` is an instance of :class:`ThesaurusIndex` as created in a `with`
    statement.

    This class should be used as a context manager, as follows::

        with ThesaurusIndex('myindex.txt') as index, \
                Thesaurus('mythesaurus.txt', index) as thesaurus:
            print(thesaurus.synonyms('cool'))

    """
    def __init__(self, filename, index):
        self.filename = filename
        self.index = index

    def __enter__(self):
        self.offsets = {}
        self.fd = open(self.filename)
        encoding = self.fd.readline()
        logging.debug('Ignoring encoding %s', encoding)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fd.close()
        # this means do not suppress exceptions raised within the context
        return False

    def synonyms(self, word, parts_of_speech=None):
        """Returns a set of synonyms for the specified word.

        If `parts_of_speech` is an iterable of strings, only synonyms of the
        specified parts of speech will be returned. The options are ``'adj'``,
        ``'noun'``, ``'verb'``, and ``'adv'``.

        """
        if parts_of_speech is None:
            parts_of_speech = ALL_PARTS_OF_SPEECH
        # Get the offset of the word in the index according to the
        # ThesaurusIndex object provided at instantiation.
        offset = self.index.byte_offset(word)
        # Set the stream position to the specified byte offset.
        self.fd.seek(offset)
        # Read the first line to determine how many lines should be read next.
        entry, num_meanings = self.fd.readline().split('|')
        # Iterate over each meaning and get all synonyms.
        result = set()
        for n in range(int(num_meanings)):
            parts = self.fd.readline().strip().split('|')
            pos = parts[0][1:-1]
            if pos not in parts_of_speech:
                continue
            meaning = parts[1]
            logging.debug('Ignoring meaning %s of word %s', meaning, word)
            related_terms = parts[1:]
            # Some related terms seem to be antonyms.
            synonyms = [term for term in related_terms
                        if not term.endswith('(antonym)')]
            # Some related terms seem to end with descriptive parentheticals,
            # so we need to strip them.
            synonyms = [term[:-15] if term.endswith('(similar term)')
                        else term for term in synonyms]
            synonyms = [term[:-15] if term.endswith('(generic term)')
                        else term for term in synonyms]
            synonyms = [term[:-15] if term.endswith('(related term)')
                        else term for term in synonyms]
            result |= set(synonyms)
        return result


def all_synonyms(thesaurus_index, thesaurus_data, words,
                 parts_of_speech=ALL_PARTS_OF_SPEECH):
    # Get all the synonyms of all the battle words.
    with ThesaurusIndex(thesaurus_index) as index, \
            Thesaurus(thesaurus_data, index) as thesaurus:
        for word in words:
            yield from thesaurus.synonyms(word, parts_of_speech)
