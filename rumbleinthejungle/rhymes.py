# rhymes.py - rhyming dictionary
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
"""Classes representing a rhyming dictionary."""
import pronouncing


class BipartiteRhymingDictionary:
    """A rhyming dictionary with left and right word sets.

    This rhyming dictionary is bipartite in the sense that words from
    the left set can only rhyme with words from the right set.

    Specifically, the :meth:`.is_rhyme` method returns ``True`` if and
    only if the words rhyme, the left word is from `words1`, and the
    right word is from `words2`.

    For example:

    .. doctest::

       >>> left = ['fool', 'cool']
       >>> right = ['pool']
       >>> rdict = BipartiteRhymingDictionary(left, right)
       >>> rdict.is_rhyme('fool', 'pool')
       True

    Implementation notes: the work of computing the rhyming parts of
    each word in the vocabulary is done at instantiation time. This uses
    a large amount of time up front in exchange for faster
    :meth:`.is_rhyme` comparisons later on. Furthermore, this class
    maintains a dictionary of the rhyming parts of each word in the
    vocabulary, which may use a large amount of memory if the vocabulary
    is large.

    .. versionadded:: 0.0.2

    """

    @staticmethod
    def _rhyming_parts(words):
        """Yield the rhyming parts of each pronunciation for each given word.

        `words` is an iterable of strings.

        This static method is an iterator generator that yields pairs
        comprising a word from `words` and a set of lists of
        strings. Each list of strings represents the rhyming part of one
        of the pronunciations of the corresponding word from `words`.

        """
        for word in words:
            phones = pronouncing.phones_for_word(word)
            yield word, set(map(pronouncing.rhyming_part, phones))

    def __init__(self, words1, words2):

        #: The rhyming part of each pronunciation of each word on the left.
        self._left = dict(BipartiteRhymingDictionary._rhyming_parts(words1))

        #: The rhyming part of each pronunciation of each word on the right.
        self._right = dict(BipartiteRhymingDictionary._rhyming_parts(words2))

    def is_rhyme(self, word1, word2):
        """Decide whether the two words rhyme.

        `word1` must be a string from the left set and `word2` must be a
        string from the right set as specified at the time of
        instantiation. The two words are considered rhyming if any
        pronunciation of the words rhymes.

        If either word is not an element of its respective vocabulary,
        this method raises a :exc:`KeyError`. For example:

        .. doctest::

           >>> left = ['fool', 'cool']
           >>> right = ['pool']
           >>> rdict = BipartiteRhymingDictionary(left, right)
           >>> rdict.is_rhyme('fool', 'cool')
           Traceback (most recent call last):
             ...
           KeyError: 'cool'

        """
        rhymingparts1 = self._left[word1]
        rhymingparts2 = self._right[word2]
        result = bool(rhymingparts1 & rhymingparts2)
        return result
