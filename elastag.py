# elastag -- storing and retrieving information according to an
#             arbitrary number of configuration options.
#
# Version 0.3, August 2012
#
# Copyright (C) 2012 Juan Reyero (http://juanreyero.com).
#
# Licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.  See the License for the specific
# language governing permissions and limitations under the
# License.
#

"""
Store objects associated to configurations defined as sets of
key-value pairs.  More restrictive configurations have more key-value
pairs.  Retrieve the object for a given query configuration that
corresponds to the most restrictive stored configuration that is a
subset of the query.

Example:

>>> el = ElasTag()
>>> el[{'lang': 'es'}] = 'es'
>>> el[{'lang': 'en'}] = 'en'
>>> el[{'lang': 'en', 'sector': 'construction'}] = 'en-construction'
>>> el[{'lang': 'en', 'sector': 'consulting'}] = 'en-consulting'
>>> el[{'lang': 'en', 'company': 'comp'}] = 'en-comp'
>>> el[{'lang': 'en', 'company': 'comp',
...     'sector': 'construction'}] = 'en-comp-construction'
>>> print el[{'lang': 'es'}]
es
>>> print el[{'lang': 'en', 'sector': 'construction'}]
en-construction
>>> print el[{'lang': 'en', 'sector': 'construction',
...           'company': 'comp'}]
en-comp-construction
>>> try:
...     print el[{'lang': 'ca'}]
... except KeyError:
...     print 'no ca'
no ca
>>> ## lang:en is the most specific configuration defined that is a subset
>>> ## of the following query:
>>> print el[{'lang': 'en', 'sector': 'retail'}]
en
>>> try:
...     print el[{'sector': 'retail'}]
... except KeyError:
...     print 'no retail without lang'
no retail without lang
>>> print {'lang': 'en', 'sector': 'construction'} in el
True
>>> ## This checks for elastic inclusion, and finds lang:en
>>> print {'lang': 'en', 'sector': 'retail'} in el
True
>>> ## This checks for exact inclusion, and does not find it.
>>> print el.haskey({'lang': 'en', 'sector': 'retail'})
False
>>> print el.haskey({'lang': 'en', 'sector': 'construction'})
True
>>> el.append({'lang': 'en', 'sector': 'construction'}, 'en-const-appended')
['en-construction', 'en-const-appended']
>>> el[{'lang': 'en', 'sector': 'construction'}]
['en-construction', 'en-const-appended']
>>> el.append({'lang': 'en', 'sector': 'retail'}, 'en-retail')
['en-retail']
>>> el.append({'lang': 'en', 'sector': 'retail'}, 'en-ret-appended')
['en-retail', 'en-ret-appended']
>>> len(el.all({'lang': 'en'}))
8
>>> el.all({'lang': 'en', 'sector': 'construction'})
['en-construction', 'en-const-appended', 'en-comp-construction']
>>> len(el.all())
9
"""


class ElasTag(dict):
    @staticmethod
    def __confid(**kw):
        ## We want them sorted, because the generated confid will be
        ## used as the key for the dictionary where objects are stored.
        return tuple([(k, kw[k]) for k in sorted(kw.keys())])

    def __translate_key(self, key):
        """Returns in tuple form the largest stored key that contains
        the incoming key.
        """
        config = set(self.__confid(**key))
        for c in sorted(self.keys(), key=len, reverse=True):
            ## We sorted reverse, so this is the largest stored
            ## configuration set that is included in config.
            if set(c) <= config:
                return c
        return None

    def __getitem__(self, key):
        config = set(self.__confid(**key))
        k = self.__translate_key(key)
        if k is not None:
            return super(ElasTag, self).__getitem__(k)
        raise KeyError('%s does not match an existing configuration' %
                       str(key))

    def __setitem__(self, key, val):
        super(ElasTag, self).__setitem__(self.__confid(**key), val)

    def __contains__(self, key):
        """Checks for elastic match.
        """
        return self.__translate_key(key)

    def haskey(self, key):
        """Checks for exact match.
        """
        return super(ElasTag, self).__contains__(self.__confid(**key))

    def append(self, key, val):
        """If key already exists, make sure it contains an array and
        append to it.  If it does not exist, create with an array.

        >>> el = ElasTag()
        >>> el.append({'lang': 'es'}, 'es1')
        ['es1']
        >>> el.append({'lang': 'es'}, 'es1')
        ['es1', 'es1']
        >>> el.bag({'lang': 'es'})
        set(['es1'])
        """
        config = self.__confid(**key)
        if super(ElasTag, self).__contains__(config):
            prev = super(ElasTag, self).__getitem__(config)
            if isinstance(prev, list):
                prev.append(val)
                return prev
            else:
                super(ElasTag, self).__setitem__(config, [prev, val])
                return [prev, val]
        else:
            super(ElasTag, self).__setitem__(config, [val])
            return [val]

    def add(self, key, val):
        """If key already exists, make sure it contains a set
        and add to it.  If it does not exist, create with a set.

        >>> el = ElasTag()
        >>> el.add({'lang': 'es'}, 'es1')
        set(['es1'])
        >>> el.add({'lang': 'es'}, 'es1')
        set(['es1'])
        >>> el.add({'lang': 'es'}, 'es2')
        set(['es2', 'es1'])
        >>> el.bag({'lang': 'es'})
        set(['es2', 'es1'])
        """
        config = self.__confid(**key)
        if super(ElasTag, self).__contains__(config):
            prev = super(ElasTag, self).__getitem__(config)
            if isinstance(prev, set):
                prev.add(val)
                return prev
            else:
                super(ElasTag, self).__setitem__(config, set([prev, val]))
                return set([prev, val])
        else:
            super(ElasTag, self).__setitem__(config, set([val]))
            return set([val])

    def all(self, key=None, as_set=False):
        """Returns an array or a set with all the elements in entries
        that have keys that include key.
        """
        if key is None:
            key = {}

        config = set(self.__confid(**key))
        out = []
        if as_set:
            out = set()
        for c in self.keys():
            if config <= set(c):
                val = super(ElasTag, self).__getitem__(c)
                if as_set:
                    if isinstance(val, set):
                        out |= val
                    elif isinstance(val, list):
                        out |= set(val)
                    else:
                        out.add(val)
                else:
                    if isinstance(val, list):
                        out += val
                    else:
                        out.append(val)
        return out

    def bag(self, key=None):
        """Returns a set with all the elements in entries that have
        keys that include key.
        """
        return self.all(key, as_set=True)


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
