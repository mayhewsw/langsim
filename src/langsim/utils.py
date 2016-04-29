import os.path
import logging
import re
from numpy.linalg import norm

__location__ = os.path.dirname(os.path.realpath(__file__))

FORMAT = "[%(asctime)s] : %(levelname)s %(filename)s.%(funcName)s():%(lineno)d - %(message)s"
DATEFMT = '%H:%M:%S, %m/%d/%Y'

logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt=DATEFMT)
logger = logging.getLogger(__name__)


class Language(object):
    """
    Language class. Each language has:

    * ISO639-1 code (e.g. tr)

    * ISO639-3 code (e.g. cmn)

    * wikipedia code (e.g. fr)

    * wikipedia name (e.g. Waray-Waray)

    * phoible data

    * wals data

    * script data

    * character frequency data

    * wikipedia file size

    """

    def __init__(self):
        self.iso3 = None
        self.wals_code = None
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
        return "L:[" + " ".join(map(lambda i: str(i), [self.iso3, self.wals_code, self.wikicode, self.wikiname])) + "]"


def readFile(fname, sep="\s+"):
    """
    Given a filename, this reads the file. This ignores any line that starts with a #
    and splits each line on `sep`. This is a very common use case.

    :param: fname name of file.
    :return: a list of lists, each list represents a line, and contains elements separated by `sep`.
    """
    out = []
    with open(fname) as f:
        for line in f:
            if line.startswith("#"):
                continue
            sline = map(lambda s: s.strip(), re.split(sep, line))
            out.append(sline)
    return out


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

def cosinec(a,b):
    """
    Cosine distance. This avoids having to install scipy.

    :param a: a numpy vector
    :param b: a numpy vector
    :return: the cosine distance between these vectors.
    """

    num = a.dot(b)
    denom = norm(a) * norm(b)

    return 1 - num/denom

