# __main__.py - finds rhyming phrases like "the dispute in Beirut"
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

from .thesaurus import ThesaurusIndex
from .thesaurus import Thesaurus
from .rhymes import BipartiteRhymingDictionary

#: The location of the thesaurus index file.
THESAURUS_INDEX = 'data/th_en_US_v2.idx'

#: The location of the thesaurus data file.
THESAURUS_DATA = 'data/th_en_US_v2.dat'

#: The location of file containing the list of cities.
CITIES_FILE = 'data/cities.dat'

#: A list of nouns that roughly mean "fight".
BATTLE_WORDS = ['fight', 'battle', 'struggle', 'tiff', 'dispute']


def rhyming_pairs(left_words, right_words):
    """Returns a set of pairs of words that rhyme.

    The left and right elements of the pair are chosen from `left_words` and
    `right_words`, respectively.

    Rhyming is determined by comparing the pronunciations of the words
    according to the Carnegie Mellon University Pronouncing Dictionary.

    """
    rdict = BipartiteRhymingDictionary(left_words, right_words)
    for word1 in left_words:
        for word2 in right_words:
            if rdict.is_rhyme(word1, word2):
                yield word1, word2


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
    synonyms = set(all_synonyms(BATTLE_WORDS))

    # Get each city name.
    cities = set(all_cities(CITIES_FILE))

    # Get each (battle, city) rhyming pair.
    pairs = rhyming_pairs(synonyms, cities)

    for word, city in pairs:
        print('the {} in {}'.format(word, city.capitalize()))


if __name__ == '__main__':
    main()
