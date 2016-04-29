wikidatastats.py
=================

This module allows interaction with Wikipedia data that has been predownloaded. Specifically, the data
is name pairs for transliteration.

The purpose of this module is to gather script statistics from all the languages, so we can get a measure of script
similarity.

We also romanized all name pairs, using `uroman <http://www.isi.edu/natural-language/software/>`_, from Ulf Hermjakob at ISI.

The wikipedia name pairs will be available for download soon.

In the future, we will also build support for reading `name pairs <http://www.clsp.jhu.edu/~anni/data/wikipedia_names>`_ described
in [Irvine2012]_.


Module Documentation
---------------------

.. automodule:: wikidatastats
   :members:


Bibliography
--------------


.. [Irvine2012] Ann Irvine, Chris Callison-Burch, and Alexandre Klementiev. "`Transliterating from All Languages <http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.297.8955&rep=rep1&type=pdf>`_" Proceedings of the Conference of the Association for Machine Translation in the Americas (AMTA). 2010.

