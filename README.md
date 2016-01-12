# Language Similarity Tools

This is a python package that measures language similarity in many different ways. Currently, we use [WALS](http://wals.info) and [Phoible](http://phoible.org) as our databases of choice.

All data files are packaged with the code.

This code is running at [stephen-mayhew.com/langsim](http://stephen-mayhew.com/langsim)

# To Install
Run

    $ git clone https://github.com/mayhewsw/langsim
    $ cd langsim
    $ python setup.py install

# To Use
`langsim.py` is the main file in this distribution. The main function to be used is `sim_overall_closest(lang)` and `sim_overall(l1, l2)`. The first returns a list of languages ranked according to similarity to `lang`, the second gets the overall similarity between `l1` and `l2`.

The arguments are ISO-639-3 language codes. Nearly every reference to language in this code is done with ISO-639-3 codes.

# Short example
```
from langsim import langsim
result = langsim.sim_closest_overall("eng")
```
`result` is a sorted list of tuples of the form:
> (overall sim, phonetic sim, script sim, genealogical sim, Language object).

`Language` class is defined in `utils.py`.

# Contribute
Feel free to fork and send pull requests!

# Related

Perhaps this should be merged with [lingpy](https://github.com/lingpy/lingpy). Also [clld](https://github.com/clld/clld) and [glottolog](http://glottolog.org/) are related. 

