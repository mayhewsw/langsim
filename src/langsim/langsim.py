import argparse
import phoible
import wals
import wikidatastats
import utils
import logging
import os.path
import uriel
import pkgutil

__location__ = os.path.dirname(os.path.realpath(__file__))

logging.basicConfig(level=logging.DEBUG, format=utils.FORMAT, datefmt=utils.DATEFMT)
logger = logging.getLogger(__name__)


def sim_script(l1, l2):
    """
    l1 and l2 are Wikipedia language names (as found in wikidata.<lang> files)
    :param l1:
    :param l2:
    :return:
    """
    langdists = wikidatastats.loaddump()
    return wikidatastats.compare(l1, l2, langdists)


def sim_script_closest(l1):
    langdists = wikidatastats.loaddump()
    closest = wikidatastats.getclosest(l1, langdists)
    return langdists, closest


def sim_gen(l1, l2):
    # get wals
    langs = wals.loadlangs()
    logger.debug(l2)
    return wals.getgensim(langs[l1], langs[l2])


def sim_gen_closest(l1):
    langs = wals.loadlangs()
    closest = wals.getclosest(l1)
    return langs, closest


def sim_phon(l1, l2):
    """
    l1 and l2 are 3 letter ISO language codes.
    :param l1:
    :param l2:
    :return:
    """
    langs = phoible.loadlangs()
    return phoible.compare(l1, l2, langs)


def sim_phon_closest(l1):
    """
    Should return a tuple: langs, closest.
    """
    #langs = phoible.loadlangs()
    #closest = phoible.getclosest(l1, langs)
    #return langs, closest

    uriel.u.loadfeatures()

    # hack!
    langlist = map(lambda p: p[0], utils.readFile("/shared/experiments/mayhew2/transliteration/tl_sim/wikinames.txt"))
    uriel.u.loadinventorysets(langlist)

    closest = uriel.getclosest(l1)
    langs = uriel.u.featlangs
    return langs, closest



def sim_overall_closest(l1, lambda1=1./3, lambda2=1./3, lambda3=1./3):
    """
    Given a language, this gets a list of close languages.
    :param l1:
    :param lambda1:
    :param lambda2:
    :param lambda3:
    :return:
    """

    phlangs,sp = sim_phon_closest(l1)

    # the keys to this are wikipedia langids!
    wikilangs,ss = sim_script_closest(l1)
    walslangs,sg = sim_gen_closest(l1)

    three2two = utils.getlangmap()

    ret = []

    # loop over languages in phoible set (which are 3 char)
    for p in sp:
        # skip if we can't get it into 2 char
        if p in three2two:
            p2 = three2two[p]
        else:
            continue

        # if the 2 char is in the wiki name list, and the 3 char is in the wals list, we're good!
        if p2 in ss and p in sg:
            phlang = utils.Language()
            phlang.iso3 = p
            ret.append((lambda1 * sp[p] + lambda2*ss[p2] + lambda3*sg[p], sp[p], ss[p2], sg[p], phlang))

    ret = sorted(ret, reverse=True)

    return ret


def sim_overall(l1, l2, lambda1=1./3, lambda2=1./3, lambda3=1./3):
    """
    This is just pairwise similarity.
    :param l1:
    :param l2:
    :param lambda1:
    :param lambda2:
    :param lambda3:
    :return:
    """
    return lambda1 * sim_phon(l1, l2) + lambda2 * sim_script(l1, l2) + lambda3 * sim_gen(l1, l2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interact with the LangSim databases.")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--sim_overall", help="Get languages ordered by similarity to query", metavar="l1", nargs=1)
    group.add_argument("--sim_overall_closest", help="Get languages ordered by similarity to query", metavar="l1", nargs=1)
    group.add_argument("--sim_gen", help="Get languages ordered by genealogical similarity", metavar=('l1', 'l2'), nargs=2)
    group.add_argument("--sim_gen_closest", help="Get languages ordered by genealogical similarity", metavar="l1", nargs='+')
    group.add_argument("--sim_script", help="Get the F1 score between l1 and l2", metavar=('l1', 'l2'), nargs='+')
    group.add_argument("--sim_phon", help="Get the Distinctive Feature score between l1 and l2", metavar=('l1', 'l2'), nargs='+')
    parser.add_argument("--highresource", "-hr", help="only compare with high resource", action="store_true")

    args = parser.parse_args()

    if args.sim_overall_closest:
        lang = args.sim_overall_closest[0]
        clo = sim_overall_closest(lang)
        print "writing to: langsim." + lang
        with open("langsim." + lang, "w") as out:
            out.write("\t".join(["# Overall", "phonetic", "script", "genealogical"]) + "\n")
            out.write("\t".join([args.sim_overall_closest[0], "1.0", "1.0", "1.0", "1.0"]) + "\n")
            for p in clo:
                n = p[-1].iso3
                out.write(n + "\t" + "\t".join(map(str, p[:-1])) + "\n")
    elif args.sim_gen:
        print sim_gen(args.sim_gen[0], args.sim_gen[1:])
    elif args.sim_script:
        print sim_script(args.sim_script[0], args.sim_script[1:])
    elif args.sim_phon:
        print sim_phon(args.sim_phon[0], args.sim_phon[1:])
    else:
        print "Oops! Not an option."

