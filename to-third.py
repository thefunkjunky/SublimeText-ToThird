import sublime
import sublime_plugin
import json
import re

settings = sublime.load_settings("ToThird.sublime-settings")
package_path = sublime.packages_path()
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
                # print("key {} value {}".format(key, value))
                # print("\nText: {}".format(str(text)))
                reobject = re.compile(key, re.I | re.M)
                text = reobject.sub(value, str(text))

        return text

