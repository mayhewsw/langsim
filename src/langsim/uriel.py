#!/usr/bin/python
import numpy as np
from collections import defaultdict
import os
import phoible
import logging

FORMAT = "[%(asctime)s] : %(filename)s.%(funcName)s():%(lineno)d - %(message)s"
DATEFMT = '%H:%M:%S, %m/%d/%Y'

logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt=DATEFMT)
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
        self.features = None
        self.langs = None


    def loaddistances(self):
        if self.distances is None:
            self.distances = np.load(urielfolder + "distances/distances.npz")

        if self.langs is None:
            self.langs = self.distances["langs"]
            
    def loadfeatures(self):
        if self.features is None:
            self.features = np.load(urielfolder + "features/features.npz")
            
        # I hope these are identical!!
        if self.langs is None:
            self.langs = self.features["langs"]

u = UrielData()

# wikilangs = set()
# with open("/shared/experiments/mayhew2/transliteration/tl_sim/wikinames.txt") as f:
#     for line in f:
#         sline = line.split()
#         if not sline[0] in langs:
#             print sline[0], "is NOT in langs"
#         else:
#             wikilangs.add(sline[0])

    
def getInventory(lang):
    """
    Get the phoneme inventory for lang from URIEL (note: this is slightly different from what is in Phoible)
    :param: an ISO639-3 language code.
    """
    u.loadfeatures()
    trumps = phoible.loadtrumps()
    
    lang_ind = np.where(u.langs==lang)

    if len(lang_ind[0]) == 0:
        print "Could not find lang:", lang
        return
    
    lfeats = u.features["data"][lang_ind][0]

    lset = defaultdict(set)

    for i,f in enumerate(u.features["feats"]):
        for j,s in enumerate(u.features["sources"]):
            if lfeats[i][j] == 1.0 and "PHOIBLE" in s and "INV" in f:
                lset[s].add(f)
                
    print lang

    inv = set()
    
    if len(lset) == 0:
        print "No inventory for lang", lang
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
            logger.debug("All sources: " + lset.keys())

            inv = lset[source]
            
    return inv

        
if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description="Interact with URIEL database")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--getInventory","-i",help="Get inventory for LANG",metavar="LANG", nargs=1)
    group.add_argument("--getF1",help="Get F1 between L1 and L2",metavar=("L1", "L2"), nargs=2)
    
    args = parser.parse_args()

    if args.getInventory:
        getInventory(args.getInventory[0])
    elif args.getF1:
        l1,l2 = args.getF1
        print l1
        print l2
        l1set= getInventory(l1)
        l2set= getInventory(l2)

        tp = len(l1set.intersection(l2set))
        fp = len(l1set - l2set)
        fn = len(l2set - l1set)

        print tp,fp,fn
        prec = tp / float(tp + fp)
        rec = tp / float(tp + fn)
        f1 = 2 * prec * rec / (prec + rec)
        print prec, rec, f1

        
