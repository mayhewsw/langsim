import sys
import os

# this needs to be here in order that the pickle loading in wikidatastats can import utils
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
sys.path.append(__location__)

__all__ = ["langsim", "phoible", "wals", "wikidatastats", "utils"]