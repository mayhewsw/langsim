from scipy.spatial.distance import cosine
import os
import codecs
import utils
from collections import defaultdict

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


class Phoneme:
    """
    This represents a phoneme, and is used when reading the language file.
    """

    def __init__(self, PhonemeID, GlyphID, Phoneme, Class, CombinedClass, NumOfCombinedGlyphs):
        self.PhonemeID = PhonemeID
        self.GlyphID = GlyphID
        self.Phoneme = Phoneme
        self.Class = Class
        self.CombinedClass = CombinedClass
        self.NumOfCombinedGlyphs = NumOfCombinedGlyphs

        # this is a printable version of Phoneme
        self.p = Phoneme.encode("utf8")

    def __repr__(self):
        return "Phoneme:[" + self.p + "]"

    def __eq__(self, other):
        return other.GlyphID == self.GlyphID

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.GlyphID.__hash__()


def loadlangs():
    """
    This takes the filename of the phoible data and reads it into useful structures.
    :param fname: the name of the phoible file, typically gold-standard/phoible-phonemes.tsv
    :return: a map of {langcode : set(phonemes), ...}, a map of {langcode : langname, ...}
    """

    fname = os.path.join(__location__, "data/phoibledata/phoible-phonemes.tsv")

    # This maps: {langcode : Language(...), ...}
    langs = {}

    with codecs.open(fname, "r", "utf-8") as p:

        i = 1

        for line in p:
            # skip header somehow?
            if i == 1:
                i += 1
                continue

            i += 1

            sline = line.split("\t")
            inventoryid = sline[0]
            langcode = sline[2]

            # trump decides between different versions
            # of the same language. 1 trumps all others.
            # FIXME: can we validate that every language has a 1? Do any start at 2?
            trump = sline[4]
            if trump != "1":
                continue

            if langcode in langs:
                lang = langs[langcode]
            else:
                lang = utils.Language()

            p = Phoneme(*sline[-6:])

            lang.phoible_set.add(p)
            lang.iso3 = langcode
            lang.name = sline[3]

            langs[langcode] = lang
            
    return langs


def loadlangdata():
    """
    This loads the file called phoible-aggregated.tsv. This has language data on each language.
    :param fname: this is the file typically called gold-standard/phoible-aggregated.tsv
    :return: a map from {langcode : {lang features}, ...}
    """
    fname = os.path.join(__location__, "data/phoibledata/phoible-aggregated.tsv")

    with open(fname) as p:
        lines = p.readlines()
        header = lines[0].split("\t")
        outdct = {}
        for line in lines[1:]:
            sline = line.split("\t")
            code = sline[2]
            ldict = dict(zip(header, sline))
            outdct[code] = ldict

    return outdct

def loadtrumps():
    """
    :return: a map from {lang : [trump1, trump2...], etc. }
    """
    fname = os.path.join(__location__, "data/phoibledata/phoible-aggregated.tsv")

    outdct = defaultdict(list)
    
    with open(fname) as p:
        lines = p.readlines()
        for line in lines[1:]:
            sline = line.split("\t")
            code = sline[2]
            trump = int(sline[6])
            source = sline[1]
            outdct[code].append((source, trump))

    # sort them here...
    for k in outdct:
        trumps = outdct[k]
        outdct[k] = map(lambda p: p[0], sorted(trumps, key=lambda p: p[1]))

    return outdct
    

def getclosest(query, langs, only_hr=False, topk=100000):
    """

    :param query: a langcode
    :param langs: the result coming from loadLangs
    :param only_hr: include only high resource languages?
    :return: a sorted list of languages sorted by similarity to the query. Format is [(highest score, langcode), (next highest, langcode), ...]
    """

    # this is a set of phonemes
    orig = langs[query]

    #hrlangs = utils.get_hr_languages()

    pmap = readfeaturefile()

    sims = {}

    for langid in sorted(langs.keys(), reverse=True):

        if langid == query:
            continue
        if True: #not only_hr or langid in hrlangs:
            # try getting F1 here instead of just intersection.
            tgt = langs[langid]

            score = getF1(orig.phoible_set, tgt.phoible_set)
            #score = getDistinctiveFeatures(orig, tgt, pmap)
            #score = getOV(tgt, orig, langs["eng"])

            sims[langid] = score

    return sims


def compare(l1, l2, langs):
    orig = langs[l1]
    tgt = langs[l2]

    score = getF1(orig, tgt)
    return score


def comparephonemes(l1, l2):
    """
    Given the phoible-phonemes file, and two langnames, this will print
    the common and unique phonemes between these languages.
    :param fname: phoible-phonemes.tsv file
    :param l1: langcode
    :param l2: langcode
    :return: None
    """

    langs = loadlangs()

    l1set = langs[l1]
    l2set = langs[l2]

    for p in l1set:
        u = p.Phoneme.decode("utf8")
        print list(u)

    print "intersection: ", l1set.intersection(l2set)
    print "unique to {0}:".format(l1), l1set.difference(l2set)
    print "unique to {0}:".format(l2), l2set.difference(l1set)


def getF1(lang1, lang2):

    """
    Get the F1 score between two sets of phonemes. This ranges from 0 to 1.
    If lang1 and lang2 are identical, the F1 is 1.
    lang1 and lang2 are phoneme sets, previously loaded by loadLangs

    :param lang1: a set of phonemes
    :param lang2: a set of phonemes
    :return: F1 score
    """

    if len(lang1) == 0:
        print "ERROR: first lang is empty or doesn't exist"
        return -1
    if len(lang2) == 0:
        print "ERROR: second lang is empty or doesn't exist"
        return -1

    tp = len(lang2.intersection(lang1))
    fp = len(lang2.difference(lang1))
    fn = len(lang1.difference(lang2))

    prec = tp / float(tp + fp)  # this is also len(tgt)
    recall = tp / float(tp + fn)  # this is also len(orig)
    f1 = 2 * prec * recall / (prec + recall)
    return f1


def readfeaturefile():
    """
    This loads the distinctive features file in phoible, typically
    called raw-data/FEATURES/phoible-segments-features.tsv
    :return: a map of {phoneme : {df : val, df : val, ...}, ...}
    """

    fname = os.path.join(__location__, "data/phoibledata/phoible-segments-features.tsv")

    i = 1
    with codecs.open(fname, "r", "utf-8") as f:
        phonememap = {}
        for line in f:

            i += 1
            sline = line.split("\t")
            phoneme = sline[0]
            feats = map(lambda v: 1 if v == "+" else 0, sline[1:])  # FIXME: currently treats unknowns as 0
            phonememap[phoneme] = feats

    return phonememap

# used for memoization.
phonedist = {}


def getdistinctivefeatures(lang1, lang2, phonemeMap):
    """
    Contrast this with getF1.

    I can't get this to work correctly.

    :param lang1: a set of Phonemes
    :param lang2: a set of Phonemes
    :return: the Distinctive Features score for these languages.
    """

    if len(lang1) == 0:
        print "ERROR: first lang is empty or doesn't exist"
        return -1
    if len(lang2) == 0:
        print "ERROR: second lang is empty or doesn't exist"
        return -1

    # loop over all pairs.
    scores = {}

    total = 0

    for p in lang1:
        # get closest in lang2
        maxsim = 0  # just a small number...
        maxp = None  # max phoneme associate with maxsim
        for p2 in lang2:
            pu1 = p.Phoneme
            pu2 = p2.Phoneme
            if pu1 in phonemeMap and pu2 in phonemeMap:

                ps = tuple(sorted([pu1, pu2]))
                if ps in phonedist:
                    sim = phonedist[ps]
                else:
                    sim = 1-cosine(phonemeMap[pu1], phonemeMap[pu2])
                    phonedist[ps] = sim
            else:
                # not there...?
                #print "SHOULD NEVER HAPPEN!",
                #if pu1 not in phonemeMap:
                #    print "missing ", pu1
                #if pu2 not in phonemeMap:
                    #print "missing ", pu2

                sim = 0
            scores[(pu1,pu2)] = sim
            total += sim

    total /= float(len(lang1) * len(lang2))

    return total


def getOV(bridge, target, eng):
    """
    This is another measure of transliterability based on overlap and
    having a richer inventory.

    :param lang1: a set of Phonemes
    :param lang2: a set of Phonemes
    :param eng: the set of Phonemes for English.
    :return: a score, larger is better.
    """
    if len(bridge) == 0:
        print "ERROR: bridge lang is empty or doesn't exist"
        return -1
    if len(target) == 0:
        print "ERROR: target lang is empty or doesn't exist"
        return -1

    common = bridge.intersection(target)
    commoneng = bridge.intersection(eng)

    bridgeonly = bridge.difference(target)
    targetonly = target.difference(bridge)

    return len(common) - len(targetonly)
    #return len(common)/float(len(target)) + len(bridgeonly) / float(len(bridge)) - len(targetonly) / float(len(target))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Interact with the Phoible database.")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--getclosest", help="Get languages ordered by similarity to lang", metavar="lang", nargs=1)
    group.add_argument("--compare", help="Compare two ")
    group.add_argument("--langdata", help="Get data for language", metavar="lang", nargs=1)
    group.add_argument("--getF1", help="Get the F1 score between lang1 and lang2", metavar=('lang1', 'lang2'), nargs=2)
    group.add_argument("--getDF", help="Get the Distinctive Feature score between lang1 and lang2", metavar=('lang1', 'lang2'), nargs=2)
    group.add_argument("--getOV", help="Get the Overlap score between lang1 and lang2", metavar=('lang1', 'lang2'), nargs=2)
    parser.add_argument("--highresource", "-hr", help="only compare with high resource", action="store_true")
    
    args = parser.parse_args()

    if args.getclosest:
        print "lang: ", args.getclosest
        langs = loadlangs()
        print getclosest(args.getclosest[0], langs, only_hr=args.highresource, topk = 10)
    elif args.getF1:
        print "langs: ", args.getF1
        langs = loadlangs()
        print getF1(langs[args.getF1[0]], langs[args.getF1[1]])
    elif args.getDF:
        print "langs: ", args.getDF
        langs = loadlangs()
        pmap = readfeaturefile()
        print getdistinctivefeatures(langs[args.getDF[0]], langs[args.getDF[1]], pmap)
    elif args.getOV:
        print "langs: ", args.getOV
        langs = loadlangs()
        print getOV(langs[args.getOV[0]], langs[args.getOV[1]], langs["eng"])
    elif args.langdata:
        print "getting langdata... for", args.langdata
        d = loadlangdata()
        print d[args.langdata[0]]

