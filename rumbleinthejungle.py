# rumbleinthejungle.py - finds rhyming phrases like "the dispute in Beirut"
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
"""Finds rhyming phrases of the form "the disput in Beirut".

"""
__version__ = '0.0.2-dev'

import functools
import itertools
import logging

from nltk.corpus import cmudict

#: The location of the thesaurus index file.
THESAURUS_INDEX = 'data/th_en_US_v2.idx'

#: The location of the thesaurus data file.
THESAURUS_DATA = 'data/th_en_US_v2.dat'

#: The location of file containing the list of cities.
CITIES_FILE = 'data/cities.dat'

#: A list of nouns that roughly mean "fight".
BATTLE_WORDS = ['fight', 'battle', 'struggle', 'tiff', 'dispute']

#: How strict the rhyming checker should be; greater is more strict.
#:
#: This integer indicates the number of "sounds" that should be compared
#: between the two strings. Since rhymes compare the rightmost sounds of words,
#: this number indicates the number of sounds to compare when counting from the
#: right.
STRICTNESS = 4

#: A set of all parts of speech known to the thesaurus.
ALL_PARTS_OF_SPEECH = {'adj', 'noun', 'verb', 'adv'}


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


def union(*sets):
    """Returns the union of all sets given as positional arguments.

    If there is exactly one positional argument, that set itself is returned.

    If there are no positional arguments, the empty set is returned.

    """
    # The last argument to reduce is the initializer used in the case of an
    # empty sequence of sets. I would like to use ``{}`` there, but Python
    # interprets that expression as a dictionary literal instead of a set
    # literal.
    #
    # This is essentially the same as ``sets[0].union(*sets[1:])``, but it
    # works even if `sets` is not a list and if `sets` has only one element.
    return functools.reduce(lambda S, T: S | T, sets, set())


def rhyming_pairs(left_words, right_words):
    """Returns a set of pairs of words that rhyme.

    The left and right elements of the pair are chosen from `left_words` and
    `right_words`, respectively. The rhyming strictness is specified by the
    :const:`STRICTNESS` constant.

    Rhyming is determined by comparing the pronunciations of the words
    according to the Carnegie Mellon University Pronouncing Dictionary.

    """
    # Create the dictionary of word pronunciations.
    pronunciations = cmudict.dict()

    # Use only those words for which cmudict knows a pronunciation.
    known_pronunciations = pronunciations.keys()
    left_words &= known_pronunciations
    right_words &= known_pronunciations

    def is_rhyme(wordpair, numsyllables=STRICTNESS):
        """Determine whether two words rhyme."""

        word1, word2 = wordpair

        # Get pronunciations of the last few syllables of each word.
        #
        # The `numsyllables` parameter controls how many of the final
        # syllables in each pronunciation are checked. Increasing the number
        # of syllables makes it more difficult to find a match.
        lastsyllables1 = {tuple(p[-numsyllables:]) for p in pronunciations[word1]}
        lastsyllables2 = {tuple(p[-numsyllables:]) for p in pronunciations[word2]}

        # Check if any of the pronunciations of the two words match.
        result = len(lastsyllables1 & lastsyllables2) > 0

        return result

    # Iterate over each possible pair of words, and compare their
    # pronunciations. If the pronunciations match, we've found a succesful
    # pair.
    pairs = filter(is_rhyme, itertools.product(left_words, right_words))

    return pairs


def all_synonyms(words):
    # Get all the synonyms of all the battle words.
    with ThesaurusIndex(THESAURUS_INDEX) as index, \
            Thesaurus(THESAURUS_DATA, index) as thesaurus:
        for word in words:
            yield from thesaurus.synonyms(word, parts_of_speech={'noun'})


def all_cities(citiesfile):
    # Get all the city names. The city names file is just a list of cities, one
    # per line.
    with open(citiesfile, encoding='utf-8', errors='ignore') as f:
        for line in f:
            yield line.strip()


def main():
    """Prints all rhyming phrases."""

    # Get each synonym for each "battle" word.
    synonyms = all_synonyms(BATTLE_WORDS)

    # Get each city name.
    cities = all_cities(CITIES_FILE)

    # Get each (battle, city) rhyming pair.
    pairs = rhyming_pairs(synonyms, cities)

    for word, city in pairs:
        print('the {} in {}'.format(word, city.capitalize()))


if __name__ == '__main__':
    main()
