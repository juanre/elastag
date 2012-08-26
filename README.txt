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
