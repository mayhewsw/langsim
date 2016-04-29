#!/usr/bin/python
from os import listdir
from os.path import isfile, join
import os.path
from collections import defaultdict
import math
import string
import argparse
import pickle
import utils
import logging

import utils

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


logging.basicConfig(level=logging.INFO, format=utils.FORMAT, datefmt=utils.DATEFMT)
logger = logging.getLogger(__name__)


def getclosest(lang, langdists):
    """
    This calculates script similarities between `lang` and all other languages in `langdists`.

    :param lang: 3-letter language code
    :param langdists: output from :func:`wikidatastats.loaddump`
    :return: a map of form {langcode : float, ...}
    """

    three2two = utils.getlangmap()
    lang2 = three2two[lang]

    langobj = langdists[lang2]
    d1 = langobj.charfreqs

    chardists = {}
    for langcode in langdists:
        if langcode == lang:
            continue

        l2obj = langdists[langcode]

        chardists[langcode] = simdist(d1, l2obj.charfreqs)

    return chardists


def loadnamemap():
    """
    Produces a map from two letter code to wikipedia name. This reads `data/wikilanguages`.

    :return: map of form {two letter code: wiki name, ...}
    """
    fname = os.path.join(__location__, "data/wikilanguages")
    code2name = {}
    with open(fname) as f:
        for line in f:
            sline = line.strip().split("\t")
            code2name[sline[1]] = sline[0]

    return code2name


def compare(langid1, langid2, langdists):
    """
    Get script similarity between languages. This just retrieves :class:`utils.Language` objects that have
    ISO codes of `langid1` and `langid2`, then calls :func:`simdist`.

    If the languages are not present in `langdists`, then the returned score is -1.

    :param langid1: 3-letter language code
    :param langid2: 3-letter language code
    :param langdists: output from :func:`wikidatastats.loaddump`
    :return: a score of script similarity
    """

    # FIXME: these should be loaded somewhere else for efficiency.
    three2two = utils.getlangmap()

    langid1 = three2two[langid1]
    langid2 = three2two[langid2]

    if langid1 not in langdists:
        print langid1, "not in langdists."
        return -1
    if langid2 not in langdists:
        print langid2, "not in langdists."
        return -1

    l1 = langdists[langid1]
    l2 = langdists[langid2]

    return simdist(l1.charfreqs, l2.charfreqs)


def simdist(d1, d2):
    """
    This gives a similarity score between character distributions. These
    character distributions are usually taken from the `charfreqs` field in :class:`utils.Language`

    :param d1: map from {character : float, ...}
    :param d2: map from {character : float, ...}
    :returns: similarity score (float)
    """

    d1norm = math.sqrt(sum(map(lambda v: math.pow(v,2), d1.values())))
    d2norm = math.sqrt(sum(map(lambda v: math.pow(v,2), d2.values())))
    
    d1chars = set(d1.keys())
    d2chars = set(d2.keys())

    common = d1chars.intersection(d2chars)
    
    dot = 0
    for char in common:
        v = math.log(d1[char]) + math.log(d2[char])
        dot += math.exp(v)

    dot /= (d1norm * d2norm)
        
    return dot


def countscripts(langdists):
    """
    This counts the number of scripts in the data. This is a convenience method
    meant to be run from the command line. It prints the results.

    The method is a bottom-up clustering. For each new language, it uses :func:`simdist`
    to get a similarity score between all previous clusters. If all scores are below a threshold
    (arbitrarily set at 0.5), then it starts a new cluster. Otherwise this language joins
    the best cluster.

    :param langdists: output from :func:`wikidatastats.loaddump`
    """
    # a list of dictionaries
    scripts = []

    for langcode in langdists:
        bestscript = None
        bestscore = -1

        langobj = langdists[langcode]
        d1 = langobj.charfreqs

        if langobj.wikisize < 100:
            continue

        # script is a dictionary
        for script in scripts:

            # just compare against the first.
            langcode2 = script.keys()[0]
            langobj2 = langdists[langcode2]
            d2 = langobj2.charfreqs

            score = simdist(d1, d2)
            if score > bestscore:
                bestscore = score
                bestscript = script

        # arbitarily set... if two languages have similar scripts
        # the similarity is usually above 0.5
        threshold = 0.5
        
        if bestscore > threshold:
            bestscript[langcode] = langobj
        else:
            scripts.append({langcode: langobj})

    for s in scripts:
        keys = s.keys()
        keysizepairs = map(lambda k: (langdists[k].wikisize, langdists[k].wikiname), keys)
        print sorted(keysizepairs)
    print "There are {0} scripts represented.".format(len(scripts))


def listsizes(limit=0):
    """
    List all the languages with size greater than limit

     :param: integer lower limit on number of lines in the data file
    """
    
    out = []
    for k in langdists.keys():
        l = langdists[k]
        if l.wikisize > int(limit):
            out.append(l)

    lm = utils.getlangmap2to3()
            
    s = sorted(out, key=lambda l: l.wikisize)
    for l in s:
        if len(l.wikicode) == 2:
            c = lm[l.wikicode]
        else:
            c = l.wikicode
        print c,l.wikiname, l.wikisize
        

def makedump(mypath, outname="data/wikilanguages.pkl"):
    """
    This collects and dumps information about every wikidata file. The name of the
    output file is

    :param mypath: is the path to the wikidata/ folder.
    """
    
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    def filtering(f):
        return f.startswith("wikidata") and len(f.split(".")) == 2
    
    onlyfiles = filter(filtering, onlyfiles)

    print "There are {0} data files in this directory.".format(len(onlyfiles))

    langdists = {}

    ignore = set(string.punctuation + string.whitespace + string.digits)

    for fname in onlyfiles:

        with open(os.path.join(mypath, fname)) as f:
            lines = f.readlines()

            lang = utils.Language()

            header = lines[0].strip("#").strip().split("\t")
            
            lang.wikisize = len(lines)
            lang.wikiname = header[0]
            lang.wikicode = header[1]
            
            charfreqs = defaultdict(int)

            for line in lines:
                sline = line.split("\t")
                foreign = sline[0].decode("utf8")
                for char in foreign:
                    if char not in ignore:
                        char = char.lower()
                        charfreqs[char] += 1

            lang.charfreqs = charfreqs
            langdists[lang.wikicode] = lang
                        
    with open(outname, "wb") as f:
        pickle.dump(langdists, f)


def loaddump(dumpname="data/wikilanguages.pkl"):
    """
    This loads a pickle file which has been previously created using :func:`wikidatastats.makedump`.
    Most importantly, the returned :class:`utils.Language` object has the `charfreqs` field set.

    :param dumpname: name of the pickle file to load from.
    :return: a map of form {wikiname : :class:`utils.Language`, ...}
    """
    fname = os.path.join(__location__, dumpname)

    with open(fname) as f:
        langdists = pickle.load(f)

    return langdists


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--listsizes", "-l", help="Print a sorted list of file sizes, include only files with size > LIMIT", metavar="LIMIT", nargs=1, default=0)
    g.add_argument("--getclosest", help="Compare LANG against all others", metavar="LANG", nargs=1)
    g.add_argument("--compare", help="Compare L1 against L2", metavar=("L1", "L2"), nargs=2)
    g.add_argument("--countscripts", help="Get a grouping of scripts", action="store_true")
    g.add_argument("--makedump", help="Create the dump", nargs=1)
    
    args = parser.parse_args()

    langdists = loaddump()
    
    if args.getclosest:
        lang = args.getclosest[0]
        print getclosest(lang, langdists)
    elif args.countscripts:        
        countscripts(langdists)
    elif args.listsizes:
        limit = args.listsizes[0]
        listsizes(limit)
    elif args.compare:
        print args.compare

        print compare(args.compare[0], args.compare[1], langdists)
    elif args.makedump:
        print args.makedump
        makedump(args.makedump[0])
    else:
        print "Whoops... argparse shouldn't let you get here"
        

