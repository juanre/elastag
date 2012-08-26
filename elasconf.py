# elasconf -- storing and retrieving information according to an
#             arbitrary number of configuration options.
#
# Version 0.1, August 2012
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
# Home page: http://juanreyero.com/open/elasconf/

"""
Store objects associated to configurations defined as sets of
key-value pairs.  More restrictive configurations have more key-value
pairs.  Retrieve the object for a given query configuration that
corresponds to the most restrictive stored configuration that is a
subset of the query.

Example:

>>> el = ElasConf()
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
>>> print el[{'lang': 'en', 'sector': 'retail'}]
en
>>> try:
...     print el[{'sector': 'retail'}]
... except KeyError:
...     print 'no retail without lang'
no retail without lang
>>> print {'lang': 'en', 'sector': 'construction'} in el
True
>>> print el.haskey({'lang': 'en', 'sector': 'construction'})
True
>>> el.append({'lang': 'en', 'sector': 'construction'}, 'appended')
['en-construction', 'appended']
>>> el[{'lang': 'en', 'sector': 'construction'}]
['en-construction', 'appended']
>>> el.append({'lang': 'en', 'sector': 'retail'}, 'en-retail')
['en-retail']
>>> el.append({'lang': 'en', 'sector': 'retail'}, 'appended')
['en-retail', 'appended']
"""

import sys

class ElasConf(dict):
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
        #sys.stderr.write(str(self.keys()))
        k = self.__translate_key(key)
        if k is not None:
            return super(ElasConf, self).__getitem__(k)
        raise KeyError('%s does not match an existing configuration' %
                       str(key))

    def __setitem__(self, key, val):
        super(ElasConf, self).__setitem__(self.__confid(**key), val)

    def __contains__(self, key):
        if self.__translate_key(key) is not None:
            return True
        return False

    ## Obsolete, but anyway.
    def haskey(self, key):
        return key in self

    def append(self, key, val):
        """If key already exists, make sure it is an array and append
        to it.  If it does not exist, create with an array.
        """
        config = self.__confid(**key)
        if super(ElasConf, self).__contains__(config):
            prev = super(ElasConf, self).__getitem__(config)
            if isinstance(prev, list):
                prev.append(val)
                return prev
            else:
                super(ElasConf, self).__setitem__(config, [prev, val])
                return [prev, val]
        else:
            super(ElasConf, self).__setitem__(config, [val])
            return [val]


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
