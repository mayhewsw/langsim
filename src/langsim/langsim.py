
import argparse
import phoible
import wals
import wikidatastats


import os.path
__location__ = os.path.dirname(os.path.realpath(__file__))

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
    langs = phoible.loadlangs()
    closest = phoible.getclosest(l1, langs)
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

    three2two = getlangmap()

    ret = []
    for p in sp:
        if p in three2two:
            p2 = three2two[p]
        else:
            continue

        phlang = phlangs[p]
        wikilang = wikilang[p2]
        walslang = walslangs[p]

        wikilang.iso3 = p

        wikilang.phoible_set = phlang.phoible_set
        wikilang.name = phlang.name

        wikilang.wals_vec = walslang.phon_feats()

        if p2 in ss and p in sg:
            ret.append((lambda1 * sp[p] + lambda2*ss[p2] + lambda3*sg[p], sp[p], ss[p2], sg[p], phlang))

    ret = sorted(ret, reverse=True)

    for r in ret:
        print r
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
    group.add_argument("--sim_overall_closest", help="Get languages ordered by similarity to query", metavar="l1", nargs=1)
    group.add_argument("--sim_overall", help="Get languages ordered by similarity to query", metavar=('l1', 'l2'), nargs=2)
    group.add_argument("--sim_gen", nargs='+')
    group.add_argument("--sim_script", help="Get the F1 score between lang1 and lang2", metavar=('lang1', 'lang2'), nargs='+')
    group.add_argument("--sim_phon", help="Get the Distinctive Feature score between lang1 and lang2", metavar=('lang1', 'lang2'), nargs='+')
    parser.add_argument("--highresource", "-hr", help="only compare with high resource", action="store_true")

    args = parser.parse_args()

    if args.sim_overall_closest:
        print sim_overall_closest(args.sim_overall_closest[0])
    elif args.sim_gen:
        print sim_gen(args.sim_gen[0], args.sim_gen[1:])
    elif args.sim_script:
        print sim_script(args.sim_script[0], args.sim_script[1:])
    elif args.sim_phon:
        print sim_phon(args.sim_phon[0], args.sim_phon[1:])

