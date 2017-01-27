import sys
import os

import json
import re
from itertools import chain

import sublime
import sublime_plugin


settings = sublime.load_settings("ToThird.sublime-settings")
package_path = sublime.packages_path()
sys.path.insert(0, "{}/ToThird/lib".format(
    package_path))
NLTK_DATA_DIR = "{}/ToThird/lib/nltk-data".format(
    package_path)

# Must use <= v3.2 of nltk, as sublime text uses old python 3.3
from nltk import download as nltk_download
# TODO: Test if nltk data exists, if not, automate nltk_download('punkt')
# TODO: Dont forget to set 'NLTK_DATA' env variable to data location
nltk_download("punkt")
from nltk.tokenize import sent_tokenize

wordmap_location = "{}/ToThird/ToThird-wordmap.json".format(
    package_path)
with open(wordmap_location, "r") as mapfile:
    mapdata = mapfile.read()
    WORDMAP = json.loads(mapdata)

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
        """  Parses sentences and fixes case with str.capitalize() """

        alphanum_list_re = r'(?<!\w)(.{1}\.)'
        teststring = "1. they are testing a numbered line."
        print("teststring: {}".format(re.split(alphanum_list_re, teststring, 1)))
        sentences = sent_tokenize(text)
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
        fixed_text = "".join(sentence[re.search("\S", sentence).start():].capitalize()
                                if re.search("\S", sentence)
                                else sentence.capitalize()
                                for sentence in sen_cleaned)

        print("fixed test: {}".format(fixed_text))

        # fixed_text = text.capitalize()

        # return fixed_text

