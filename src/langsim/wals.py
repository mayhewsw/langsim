import argparse
import csv
import numpy as np
import os.path
import utils

# Phonology index range (strict python indexing)
from scipy.spatial.distance import cosine

PHON_INDS = (0,19)

# Morphology index range (strict python indexing)
MORPH_INDS = (19,31)

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


class WALSLanguage(utils.Language):
    """
    This represents a single language in the WALS system. This contains a feature
    vector for the WALS features.
    """

    def mp(self, x):
        """
        This turns the WALS vector into an integer vector. Each feature
        has the format: <int> <Description>.
        This just returns the int.
        """
        out = []
        for v in x:
            if len(v) == 0:
                out.append(0)
            else:
                out.append(int(v[0]))
        return out

    def __init__(self, header, walslist):
        super(WALSLanguage, self).__init__()

        # Store everything
        self.dctzip = zip(header, walslist)
        self.dct = dict(self.dctzip)

        # WALS feats
        self.feats = self.mp(walslist[10:])

        # lat and long
        self.coords = (walslist[4], walslist[5])

    def __getitem__(self, item):
        return self.dct[item]

    def phon_feats(self):
        return self.feats[slice(*PHON_INDS)]

    def morph_feats(self):
        return self.feats[slice(*MORPH_INDS)]

    # def __repr__(self):
    #     return "Language " + self.dct["Name"]

    def fullname(self):
        return self.dct["Name"] + ":" + self.dct["genus"] + ":" + self.dct["family"]

    def name(self):
        return self.dct["Name"]


def loadlangs():
    """
    This loads the WALS file into the WALSLanguage data structures
    :return: list of WALSLanguage objects
    """

    fname = os.path.join(__location__, "data/walsdata/language.csv")

    #hrlangs = utils.get_hr_languages()
        
    with open(fname) as csvfile:
        f = csv.reader(csvfile, delimiter=',', quotechar='"')

        langs = {}

        header = f.next()
        # wals features begin at index 10
        #FIXME: this is ugly!!!
        maxvals = np.zeros(len(header[10:]))
        for line in f:
            lang = WALSLanguage(header, line)

            maxvals = np.maximum(maxvals, lang.feats)

            #if lang["iso_code"] in hrlangs:
            #    lang.hr = True

            lang.iso3 = lang["iso_code"]
            langs[lang["iso_code"]] = lang

        # normalize each feature by the maximum possible value.
        for langcode in langs.keys():
            lang = langs[langcode]
            lang.feats = lang.feats / maxvals

        return langs


def getphonsim(l1, l2):
    """
    This gets the average number of identical values between vectors.
    :param l1: a WALSLanguage
    :param l2: a WALSLanguage
    :return: a similarity value between 0 (not similar) and 1 (most similar)
    """

    tgtf = l1.phon_feats()
    t = l2.phon_feats()

    # this would be the best method, but we have to deal with missing values.
    #dist = cosine(tgtf, t)

    # number of elements where they are equal
    numequal = sum(np.equal(tgtf, t))

    # now remove all places where they are both zero
    a = set(np.where(tgtf == 0)[0])
    b = set(np.where(t == 0)[0])

    numequal -= len(a.intersection(b))

    sim = numequal / float(len(tgtf))
    return sim


def getgensim(l1, l2):
    """
    Get genealogical similarity between languages. These are WALSLanguage objects.
    :param l1:
    :param l2:
    :return:
    """

    sim = 0
    if l1["family"] == l2["family"]:
        sim = 0.5
        if l1["genus"] == l2["genus"]:
            sim = 1
    return sim


def getclosest(lang, threshold=0, only_hr=False, topk=20):
    """
    Gets a topk list of languages similar to this language, various parameters control this.
    :param lang:
    :param threshold:
    :param only_hr:
    :param topk:
    :return:
    """

    langs = loadlangs()

    tgtlang = langs[lang]

    if tgtlang == None:
        return [(-1, "Language '{0}' not found...".format(lang.encode("utf8")))]

    # now filter by high resource
    # get tgtlang first, b/c it may not be high resource
    if only_hr:
        langs = filter(lambda l: l.hr, langs)

    sims = {}

    for lcode in langs.keys():
        l = langs[lcode]
        if l["iso_code"].decode("utf8") == lang:
            continue

        #sim = getphonsim(tgtlang, l)
        sim = getgensim(tgtlang, l)

        sims[lcode] = sim

    #sims = sorted(sims, reverse=True)

    return sims


def compare(lang1, lang2):
    """
    Given two language names, get distance according to phonology scores.
    :param lang1: name of first lang (eg English)
    :param lang2: name of second lang
    :return: the distance of the languages, or -1 if one or both langs not found.
    """
    l1, l2 = comparefeats(lang1, lang2)

    if l1 and l2:
        return cosine(l1.phon_feats(),l2.phon_feats())
    else:
        print "One or both langs not found: {0}, {1}".format(l1, l2)
        return -1


def comparefeats(lang1, lang2):
    """
    What does this do???
    :param lang1:
    :param lang2:
    :return:
    """
    langs = loadlangs()

    l1 = None
    l2 = None
    for lang in langs:
        if lang["Name"].decode("utf8") == lang1:
            l1 = lang
        elif lang["Name"].decode("utf8") == lang2:
            l2 = lang

    return l1, l2

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Interact with the WALS database.")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--getclosest", help="Get languages ordered by similarity to lang", metavar="lang", nargs=1)
    group.add_argument("--getgensim", help="Get genealogical similarity", nargs=2)
    parser.add_argument("--highresource", "-hr", help="only compare with high resource", action="store_true")

    args = parser.parse_args()

    if args.getclosest:
        print "lang: ", args.getclosest
        print getclosest(args.getclosest[0], only_hr=args.highresource, topk=10)
    elif args.getgensim:
        langs = loadlangs()

        print getgensim(langs[args.getgensim[0]], langs[args.getgensim[1]])

