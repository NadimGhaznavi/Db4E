

import os

from textual.app import App
from textual.widgets import Label, Input, Button
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.message import Message

class TargetDir(Message):
    def __init__(self, sender, target_dir):
        self.target_dir = target_dir

class LsForm:
    def compose(self):
        yield Horizontal(
            Label('Enter a directory: '),
            Input(restrict=r"/[a--zA-Z0-9/_.\- ]*", id="target_dir"),
        )
        yield Button(label="List Contents", id="run_ls")

    def on_button_pressed(self, event):
        target_dir = self.query_one("#target_dir", Input).value
        self.post_message(TargetDir(self, target_dir))

class RunLs:
    def get_contents(self, target_dir):
        return os.listdir(target_dir) # returns a list

class LsResults:
    contents = reactive([])
    def __init__(self, results=None):
        self.results = results

    def compose(self):
        yield Label('Directory Contents:')
        for aDir in self.results:
            Label(aDir)

    def set_contents(self, contents):
        self.contents = contents

class Ls(App):

    def __init__(self):
        self.form = LsForm()
        self.run_ls = RunLs()
        self.results = LsResults()

    def compose(self):
        yield self.form
        #yield self.results

    def on_target_dir(self, message):
        target_dir = message.target_dir
        dir_contents = self.run_ls.get_contents(target_dir)
        self.results.set_contents(dir_contents)

if __name__ == "__main__":
    app = Ls()
    app.run()

        

