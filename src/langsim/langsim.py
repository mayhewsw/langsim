import pkgutil
import argparse
import phoible
import wals
import wikidatastats

import os.path
__location__ = os.path.dirname(os.path.realpath(__file__))

# FIXME: consider having a Language class here.

class Language:

    # each language has: ISO639-1 code, ISO639-3 code, wikipedia code, wikipedia name,
    # phoible data
    # wals data
    # script data
    # wikipedia file size
    #
    pass

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


def sim_script(l1, l2=[]):
    """
    l1 and l2 are Wikipedia language names (as found in wikidata.<lang> files)
    :param l1:
    :param l2:
    :return:
    """

    if len(l2) > 0:
        print "script sim between {0} and {1}".format(l1, l2)
        # get script stuff
        l2 = l2[0]

        sizes, langdists = wikidatastats.loaddump()
        score = wikidatastats.compare(l1, l2, langdists)

        return score
    else:
        print "script sim between {0} and all the rest".format(l1)
        return 0


def sim_gen(l1, l2=[]):
    # get wals

    if len(l2) > 0:
        print "gen sim between {0} and {1}".format(l1, l2)
        l2 = l2[0]

        langs = wals.loadlangs()

        return wals.getgensim(langs[l1], langs[l2])
    else:
        print "gen sim between {0} and all the rest".format(l1)
        return 0


def sim_phon(l1, l2=[]):
    """
    l1 and l2 are 3 letter ISO language codes.
    :param l1:
    :param l2:
    :return:
    """

    # get phoible
    if len(l2) > 0:
        print "phon sim between {0} and {1}".format(l1,l2)
        l2 = l2[0]
        langs,code2name = phoible.loadlangs()
        return phoible.compare(l1, l2, langs)

    else:
        print "phon sim between {0} and all the rest".format(l1)
        return 0


def sim_overall(l1, l2=[], lambda1=1./3, lambda2=1./3, lambda3=1./3):
    return lambda1 * sim_phon(l1,l2) + lambda2 * sim_script(l1,l2) + lambda3 * sim_gen(l1,l2)


def getclosest(l1, l2=[]):
    # but what languages here??
    # use sim_overall to get this... but what languages?
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interact with the Phoible database.")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--sim_overall", help="Get languages ordered by similarity to query", metavar="query", nargs='+')
    group.add_argument("--sim_gen", nargs='+')
    group.add_argument("--sim_script", help="Get the F1 score between lang1 and lang2", metavar=('lang1', 'lang2'), nargs='+')
    group.add_argument("--sim_phon", help="Get the Distinctive Feature score between lang1 and lang2", metavar=('lang1', 'lang2'), nargs='+')
    parser.add_argument("--highresource", "-hr", help="only compare with high resource", action="store_true")

    args = parser.parse_args()

    if args.sim_overall:
        print sim_overall(args.sim_overall[0], args.sim_overall[1:])
    elif args.sim_gen:
        print sim_gen(args.sim_gen[0], args.sim_gen[1:])
    elif args.sim_script:
        print sim_script(args.sim_script[0], args.sim_script[1:])
    elif args.sim_phon:
        print sim_phon(args.sim_phon[0], args.sim_phon[1:])

