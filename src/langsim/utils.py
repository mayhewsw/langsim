import os.path
import pkgutil

__location__ = os.path.dirname(os.path.realpath(__file__))


class Language(object):
    """
    Language class
    """
    # each language has: ISO639-1 code, ISO639-3 code, wikipedia code, wikipedia name,
    # phoible data
    # wals data
    # script data
    # wikipedia file size

    def __init__(self):
        self.iso3 = None
        self.iso1 = None
        self.wikicode = None
        self.wikiname = None
        self.wikisize = None
        self.wals_vec = None
        self.phoible_set = set()
        self.charfreqs = None
        self.name = None
        self.alternate_names = set()

    def __repr__(self):
        return "L:[" + " ".join(map(lambda i: str(i), [self.iso3, self.iso1, self.wikicode, self.wikiname])) + "]"


def loadLangs():

    # data/wals



    
    pass


    
def getmissingmap():
    """
    Get the map of languages missing from Phoible
    """
    with open("data/missing.map") as f:
        lines = f.readlines()
    m = {}
    for line in lines:
        if line.startswith("#"):
            continue
        missing,target = line.strip().split()
        if "," in target:
            # just take the first one...
            target = target.split(",")[0]
        m[missing] = target
    return m

def getlangmap():
    """
    This produces a map from ISO 639-3 codes to ISO 639-1 codes. Sigh.
    :return:
    """

    fname = os.path.join(__location__, "data/iso-639-3_20150505.tab")

    three2two = {}
    with open(fname) as f:
        for line in f:
            sline = line.split("\t")

            # if the ISO639-1 code is not there, just map to the 3 letter code.
            twoletter = sline[3]
            if len(twoletter.strip()) == 0:
                twoletter = sline[0]
            three2two[sline[0]] = twoletter

    return three2two

def getlangmap2to3():
    """
    This produces a map from ISO 639-3 codes to ISO 639-1 codes. Sigh.
    :return:
    """

    fname = os.path.join(__location__, "data/iso-639-3_20150505.tab")

    two2three = {}
    with open(fname) as f:
        for line in f:
            sline = line.split("\t")

            # if the ISO639-1 code is not there, just map to the 3 letter code.
            twoletter = sline[3]
            if len(twoletter.strip()) > 0:
                two2three[twoletter] = sline[0]

    return two2three
