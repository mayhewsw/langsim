#!/usr/bin/python
from os import listdir
from os.path import isfile, join
import os.path
from collections import defaultdict
import math
import string
import argparse
import pickle
import langsim

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


class StaticStats:

    def __init__(self):

        sizes, langdists = loaddump()
        self.sizes = sizes
        self.langdists = langdists


def getclosest(lang, langdists):
    pass


def loadnamemap():
    """
    Produces a map from two letter code to wikipedia name
    :return:
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
    Get score for these two
    :param langid1:
    :param langid2:
    :return: a score of script similarity
    """

    # FIXME: these should be loaded somewhere else for efficiency.
    m = loadnamemap()
    three2two = langsim.getlangmap()

    langname1 = m[three2two[langid1]]
    langname2 = m[three2two[langid2]]

    def f(i):
        return "wikidata." + i

    if f(langname1) not in langdists:
        print langname1, "not in langdists. (This means there is no wikidata.{0} file)".format(langname1)
        return -1
    if f(langname2) not in langdists:
        print langname2, "not in langdists. (This means there is no wikidata.{0} file)".format(langname2)
        return -1

    l1 = langdists[f(langname1)]
    l2 = langdists[f(langname2)]

    return simdist(l1, l2)


def simdist(d1, d2):
    """
    d1 and d2 are each dictionaries as {char:freq, ...}
    This gives a similarity score between them.
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


def countscripts(sizes,langdists):
    # a list of dictionaries
    scripts = []

    dsizes = dict(sizes)

    # this reverses sizes and makes it a dictionary
    # new format: {lang:size, lang:size...}
    dictsizes = dict([(p[1],p[0]) for p in sizes])
    
    for fname in langdists.keys():
        bestscript = None
        bestscore = -1

        d1 = langdists[fname]
        
        if dictsizes[fname] < 100:
            continue
        
        # script is a dictionary
        for script in scripts:

            fname2 = script.keys()[0]
            d2 = langdists[fname2]
            
            score = simdist(d1,d2)
            if score > bestscore:
                bestscore = score
                bestscript = script
        threshold = 0.004
        
        if bestscore > threshold:
            bestscript[fname] = langdists[fname]
        else:
            scripts.append({fname : langdists[fname]})


    for s in scripts:
        keys = s.keys()
        keysizepairs = map(lambda k: (dictsizes[k],k), keys)
        print sorted(keysizepairs)
    print "There are {0} scripts represented.".format(len(scripts))
            

def makedump(mypath):
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    def filtering(f):
        return f.startswith("wikidata") and len(f.split(".")) == 2
    
    onlyfiles = filter(filtering, onlyfiles)

    print "There are {0} data files in this directory.".format(len(onlyfiles))

    sizes = []
    langdists = {}

    ignore = set(string.punctuation + string.whitespace + string.digits)
    
    for fname in onlyfiles:
        with open(fname) as f:
            lines = f.readlines()
            sizes.append((len(lines),fname))

            charfreqs = defaultdict(int)

            for line in lines:
                sline = line.split("\t")
                foreign = sline[0].decode("utf8")
                for char in foreign:
                    if char not in ignore:
                        char = char.lower()
                        charfreqs[char] += 1
                    
            langdists[fname] = charfreqs
                        
    sizes = sorted(sizes,reverse=True)

    # should this be "wb"?
    with open("sizes-langdists.pkl", "w") as f:
        pickle.dump(sizes, langdists, f)


def loaddump():
    fname = os.path.join(__location__, "data/sizes-langdists.pkl")

    f = open(fname)
    sizes, langdists = pickle.load(f)
    f.close()
    return sizes, langdists


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--listsizes", help="Print a sorted list of file sizes", action="store_true")
    g.add_argument("--getclosest", help="Compare LANG against all others", nargs=1)
    g.add_argument("--compare", help="Compare LANG1 against LANG2", nargs=2)
    g.add_argument("--countscripts", help="Get a grouping of scripts", action="store_true")
    
    args = parser.parse_args()

    sizes,langdists = loaddump()

    if args.getclosest:
        lang = args.getclosest[0]
        d1 = langdists["wikidata." + lang]
        
        chardists = []
        for fname in langdists:
            if fname == "wikidata." + lang:
                continue
            chardists.append((simdist(d1, langdists[fname]), fname))

        st = sorted(chardists, reverse=True)
        topk = 20
        for p in st[:topk]:
            print p
    elif args.countscripts:        
        countscripts(sizes,langdists)
    elif args.listsizes:
        for p in sizes:
            print p[1],p[0]
    elif args.compare:
        print args.compare
        # why are first and second
        #d1 = langdists["wikidata." + args.compare[0]]
        #d2 = langdists["wikidata." + args.compare[1]]

        #print simdist(d1, d2)

        print compare(args.compare[0], args.compare[1], langdists)

    else:
        print "Whoops... argparse shouldn't let you get here"
        
        


    
