Getting Started
================

From Github
-------------

This project is on `Github <https://github.com/mayhewsw/langsim>`_. Get the source::

    $ git clone https://github.com/mayhewsw/langsim


Compressed
-----------

* `tarball <https://github.com/mayhewsw/langsim/tarball/master>`_

* `zipball <https://github.com/mayhewsw/langsim/zipball/master>`_


Data
-----

This project depends on data from URIEL, WALS, and Phoible. The WALS and Phoible data are included (in the `data folder <https://github.com/mayhewsw/langsim/tree/master/src/langsim/data>`_`)
but the URIEL data is too large. Get it `here <http://www.cs.cmu.edu/~dmortens/downloads/uriel_v0_3_0.tar.xz>`_. Alternatively,
run the following::

    $ wget http://www.cs.cmu.edu/~dmortens/downloads/uriel_v0_3_0.tar.xz
    $ tar xvf uriel_v0_3_0.tar.xz

Now open up `uriel.py <https://github.com/mayhewsw/langsim/blob/master/src/langsim/uriel.py>`_, and set the `urielfolder` variable to the correct location. I typically install URIEL into the
data/ folder, but this is up to you.

Dependencies
------------

This depends on numpy and scipy::

    $ pip install numpy
    $ pip install scipy


