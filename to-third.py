import sys
import os

import json
import re
from itertools import chain

import sublime
import sublime_plugin


settings = sublime.load_settings("ToThird.sublime-settings")

# Set library PATH, NLTK Data Directory, load WORDMAP and ABBREV, etc.
package_path = sublime.packages_path()
sys.path.insert(0, "{}/ToThird/lib".format(
    package_path))
NLTK_DATA_DIR = "{}/ToThird/lib/nltk-data".format(
    package_path)
wordmap_location = "{}/ToThird/ToThird-wordmap.json".format(
    package_path)
abbrev_location = "{}/ToThird/ToThird-abbrevs.json".format(
    package_path)

with open(wordmap_location, 'r') as mapfile:
    mapdata = mapfile.read()
    WORDMAP = json.loads(mapdata)
with open(abbrev_location, 'r') as abbrev_file:
    abbrevdata = abbrev_file.read()
    ABBREV = json.loads(abbrevdata)


# Import NLTK Punkt and download training data file
# Must use <= v3.2 of nltk, as sublime text 3 uses old python 3.3
from nltk import download as nltk_download
from nltk.tokenize import sent_tokenize
from nltk.tokenize.punkt import (PunktSentenceTokenizer,
                                PunktParameters,
                                PunktLanguageVars)
nltk_download("punkt")

class CustomLanguageVars(PunktLanguageVars):
    """ Customized Punkt CustomLanguageVars _period_context_fmt 
    for the purpose of retaining trailing spaces (and newlines?)
    in tokenized sentences"""
    _period_context_fmt = r"""
        \S*                          # some word material
        %(SentEndChars)s             # a potential sentence ending
        \s*                       #  <-- THIS is what I changed
        (?=(?P<after_tok>
            %(NonWord)s              # either other punctuation
            |
            (?P<next_tok>\S+)     #  <-- Normally you would have \s+ here
        ))"""


def punkt_tokenize(text):
    """ Method to init Punkt, set params, and return tokenized text """
    try:
        tokenizer
    except NameError:
        punkt_param = PunktParameters()
        abbreviation = ABBREV
        punkt_param.abbrev_types = set(abbreviation)
        tokenizer = PunktSentenceTokenizer(punkt_param,
                                            lang_vars=CustomLanguageVars())
    tokenized_text = tokenizer.tokenize(text)
    return tokenized_text

def sentence_cleanup(sentences):
    """ Performs various cleanup operations on a list of sentences
    parsed by nltk Punkt for the purposes of mitigating errors encountered
    due to Punkt's limitations in certain edge-cases """

    #####
    # Regex patterns
    #####
    # Catch ellipses ("...")
    # TODO: This results in following string being capitalized incorrectly
    # TODO: Note that this wouldn't be needed if alphanum_list_re worked better
    ellipses_re = r"(\.\.\.)"
    # TODO: This regex needs to be fixed.
    # Catch alphanumeric lists (1. blah, a) Blah, 123. Blah)
    alphanum_list_re = r"(?<!\w)(\A|\n)([a-zA-Z0-9]+[\.|\)]{1})(?!\.)( )*"

    # teststring = "1. Mr. Jennings is testing a numbered line."
    # print("teststring: {}".format(re.split(alphanum_list_re, teststring)))
    sen_split_ellipses = [re.split(ellipses_re, sentence)
                                for sentence in sentences]
    # Flatten nested lists
    sen_split_ellipses = list(chain(*sen_split_ellipses))
    # print("sen_split_ellipses: {}".format(sen_split_ellipses))

    sen_split_alphanum_list = [re.split(alphanum_list_re, sentence)
                                for sentence in sentences]
    # print("sen_split_alphanum_list: {}".format(sen_split_alphanum_list))
    sen_cleaned = list(chain(*sen_split_alphanum_list))
    print("sen_cleaned: {}".format(sen_cleaned))
    # for sentence in sentences:
    #     if sentence[-1] == "\n":
    #         delimiter = "\n"
    #     else:
    #         delimiter = " "
    fixed_text = "".join(sentence[
                    re.search("[a-zA-Z]", sentence).start():]
                    .capitalize()
                    if re.search("[a-zA-Z]", sentence)
                    else sentence.capitalize()
                    for sentence in sen_cleaned)

    # TODO: capitalize title abbreviations (Mr., Mrs., etc.)

    return fixed_text


class ToThirdPerson(sublime_plugin.TextCommand):
    """ Main class for To Third (person) sublime text 3 package """
    def run(self, edit):
        """ Launch method for ToThirdPerson plugin"""
        for region in self.view.sel():
            if region.empty and settings.get(
                    "use_entire_file_if_no_selection", True):
                selection = sublime.Region(0, self.view.size())
            else:
                # This does not appear to work
                selection = region

            try:
                selection_text = self.view.substr(selection)
                converted_text = self.to_third(selection_text)
                self.view.replace(edit, selection, converted_text)
            except Exception as e:
                print("Failed with exception {}".format(e))

    def to_third(self, text):
        """  Inputs text, search and replace for pattern matches,
        and returns modified text."""
        operations_ordered = ['conjunctions', 'multi-word', 'single-word']
        for op in operations_ordered:
            for key, value in WORDMAP[op].items():
                reobject = re.compile(key, re.I | re.M)
                text = reobject.sub(value, str(text))

        fixed_text = self.fix_case(text)
        return fixed_text

    def fix_case(self, text):
        """  Parses sentences and fixes case """

        # TODO: Read the following and figure out how to preserve spaces:
        # TODO: http://stackoverflow.com/questions/33139531/preserve-empty-lines-with-nltks-punkt-tokenizer
        sentences = punkt_tokenize(text)
        print("Punkt sentences: {}".format(sentences))

        fixed_text = sentence_cleanup(sentences)

        print("fixed test: {}".format(fixed_text))

        # fixed_text = text.capitalize()

        # return fixed_text

