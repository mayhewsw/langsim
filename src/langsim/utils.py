import os.path
import pkgutil

__location__ = os.path.dirname(os.path.realpath(__file__))

class Language(object):
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

    def __repr__(self):
        if self.iso3:
            return "L:" + self.iso3
        else:
            return "L:?"


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


def get_hr_languages(hrthreshold=0):
    """
    :param fname: the name of the file containing filesizes. Created using wc -l in the wikidata folder
    :param hrthreshold: how big a set of transliteration pairs needs to be considered high resource
    :return: a map of language names (in ISO 639-3 format?)
    """

    lines = pkgutil.get_data('langsim', 'data/langsizes.txt').split("\n")

    hrlangs = {}
    for line in lines:
        if len(line.strip()) == 0:
            continue
        longname, iso639_3, iso639_1, size = line.strip().split()
        if int(size) > hrthreshold:
            hrlangs[iso639_3] = longname
    return hrlangs