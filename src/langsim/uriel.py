#!/usr/bin/python
import numpy as np
from collections import defaultdict
import os
import phoible
import utils
import logging

logging.basicConfig(level=logging.INFO, format=utils.FORMAT, datefmt=utils.DATEFMT)
logger = logging.getLogger(__name__)

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
urielfolder = os.path.join(__location__, "data/uriel_v0_3_0/")


class UrielData:
    """
    This is intended to act as a container for uriel data. This is a global object,
    and you can load parts of it as necessary, e.g. distances, or features.
    """
    
    def __init__(self):
        self.distances = None
        self.distlangs = None
        self.features = None
        self.featlangs = None
        self.invsets = None

        self.phoiblesources = None
        self.phoiblefeats = None
        self.invsets = None

    def loaddistances(self):
        if self.distances is None:
            self.distances = np.load(urielfolder + "distances/distances.npz")

        if self.distlangs is None:
            self.distlangs = self.distances["langs"]
            
    def loadfeatures(self):
        if self.features is None:
            self.features = np.load(urielfolder + "features/features.npz")
            
        # I hope these are identical!!
        if self.featlangs is None:
            self.featlangs = self.features["langs"]

    def getphoibleindices(self):
        self.phoiblefeats = []
        for i,f in enumerate(u.features["feats"]):
            if "INV" in f:
                self.phoiblefeats.append((i,f))

        self.phoiblesources = []
        for j,s in enumerate(u.features["sources"]):
            if "PHOIBLE" in s:
                self.phoiblesources.append((j,s))

    def loadinventorysets(self, langlist=None):
        """
        This loads inventory sets. The form is:
        {lang : {source : set(seg, ...), ...}, ...}
        """

        if self.invsets is None:
            self.invsets = {}
            self.loadfeatures()
            self.getphoibleindices()

            logger.info("Loading inventory sets...")
            logger.debug("Langlist: " + str(langlist))

            enum = zip(range(len(self.featlangs)), self.featlangs)

            if langlist is not None:
                newenum = []
                for l,lang in enum:
                    if lang in langlist:
                        newenum.append((l,lang))
                enum = newenum

            d = u.features["data"]

            for l, lang in enum:
                lfeats = d[l]

                logger.debug("Loading %s", lang)

                lset = defaultdict(set)

                for i, f in u.phoiblefeats:
                    lfeatsi = lfeats[i]
                    for j,s in u.phoiblesources:
                        if lfeatsi[j] == 1.0:
                            lset[s].add(f)

                self.invsets[lang] = lset

u = UrielData()
trumps = phoible.loadtrumps()

def getclosest(query):
    """
    get closest in here...
    """

    # this is a set of phonemes
    orig = getInventory(query)

    sims = {}

    for langid in u.invsets.keys():

        if langid == query:
            continue

        # try getting F1 here instead of just intersection.
        tgt = getInventory(langid)

        score = phoible.getF1(orig, tgt)
        #score = getDistinctiveFeatures(orig, tgt, pmap)
        #score = getOV(tgt, orig, langs["eng"])

        sims[langid] = score

    return sims


def getInventory(lang):
    """
    Get the phoneme inventory for lang from URIEL (note: this is slightly different from what is in Phoible)

    :param: an ISO639-3 language code.
    :return: a set of inventory strings.
    """

    if u.invsets is None:
        logger.error("u.invsets is None. Initialize with u.loadinventorysets()")
        return set()

    if lang not in u.invsets:
        logger.error("Could not find lang: " + lang)
        return

    lset = u.invsets[lang]

    logger.debug("Loading: " + lang)

    inv = set()
    
    if len(lset) == 0:
        logger.error("No inventory for lang: " + lang)
    elif len(lset) == 1:
        source = lset.keys()[0]
        logger.debug("Only source: " + source)
        inv = lset[source]
    else:

        if lang in trumps:
            bestsource = "PHOIBLE_" + trumps[lang][0]
            logger.debug("Selecting source: " + bestsource)
            inv = lset[bestsource]
            
            logger.debug("Others:")
            for k in trumps[lang][1:]:
                logger.debug("PHOIBLE_" + k)
                logger.debug(len(lset["PHOIBLE_" + k]))
        else:
            logger.debug(lang + " not in trumps, just taking first source...")
            source = lset.keys()[0]
            logger.debug("All sources: " + str(lset.keys()))

            inv = lset[source]
            
    return inv

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description="Interact with URIEL database")

    parser.add_argument("--langlist", "-l", help="A file containing a list of languages to use", nargs=1)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--getInventory", "-i", help="Get inventory for LANG", metavar="LANG", nargs=1)
    group.add_argument("--getF1", help="Get F1 between L1 and L2", metavar=("L1", "L2"), nargs=2)
    group.add_argument("--getClosest", help="Get closest langs to L", metavar="L", nargs=1)
    
    args = parser.parse_args()

    # langlist represents a list of languages to use.
    if args.langlist:
        lines = map(lambda s: s[0], utils.readFile(args.langlist[0], sep=" "))
        u.loadinventorysets(lines)
    else:
        u.loadinventorysets()

    if args.getInventory:
        getInventory(args.getInventory[0])
    elif args.getF1:
        l1, l2 = args.getF1

        l1set = getInventory(l1)
        l2set = getInventory(l2)

        print phoible.getF1(l1set, l2set)
    elif args.getClosest:
        lang = args.getClosest[0]
        c = getclosest(lang)
        ci = sorted(c.items(), key=lambda p: p[1], reverse=True)
        logger.info("Writing to mine." + lang)
        with open("mine." + lang, "w") as out:
            out.write(lang + "\t1.0\n")
            ignored = 0
            iset = set()
            for l in ci:
                if l[1] >= 0:
                    out.write(l[0] + "\t" + str(l[1]) + "\n")
                else:
                    iset.add(l[0])
                    ignored += 1
            print iset
            logger.info("Ignored {0}/{1} languages.".format(ignored, len(ci)))


