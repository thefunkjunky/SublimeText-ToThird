import sublime
import sublime_plugin


class FirstToThirdPerson(sublime_plugin.TextCommand):
    def run(self, edit):
        allcontent = sublime.Region(0, self.view.size())
        self.view.replace(edit, allcontent, 'Hello, world!')
