import sublime
import sublime_plugin
import json

# settings = sublime.load_settings("ToThird.sublime-settings")
package_path = sublime.packages_path()
sublime.status_message(package_path)
wordmap_location = "{}/ToThird/ToThird-wordmap.json".format(
    package_path)
with open(wordmap_location, "r") as mapfile:
    mapdata = mapfile.read()
    WORDMAP = json.loads(mapdata)


class ToThirdPerson(sublime_plugin.TextCommand):
    """ Main class for To Third (person) sublime text 3 package """
    def run(self, edit):
        allcontent = sublime.Region(0, self.view.size())
        selects = self.view.sel()
        # Check for selections and run to_third() on them, otherwise run it on
        # whole document
        if selects:
            for select in selects:
                self.view.replace(edit, select, self.to_third(select))
        else:
            self.view.replace(edit, allcontent, self.to_third(select))

    def to_third(self, text):
        """  Inputs text, search and replace for pattern matches,
        and returns modified text."""

        pass
