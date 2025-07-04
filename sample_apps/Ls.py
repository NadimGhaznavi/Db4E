import os

from rich.text import Text
from textual.app import App
from textual.widgets import Label, Input, Button, Pretty
from textual.containers import Container, Horizontal, Vertical
from textual.message import Message

class TargetDirectory(Message):
    def __init__(self, directory):
        super().__init__()
        self.directory = directory


class LsForm(Container):
    def compose(self):
        yield Vertical(
            Horizontal(
                Label("Directory:", id="input_label"),
                Label(' '),
                Input(compact=True, restrict=r"/[a-zA-Z0-9/_.\- ]*", id="input_field"),
                Label(' '),
                Button(label="Enter", compact=True, id="input_button"),
                id="input_line"
            ),
            id="input_screen"
        )
    
    def on_button_pressed(self, event):
        directory = self.query_one("#input_field", Input).value
        self.post_message(TargetDirectory(directory))


class LsHeader(Container):

    def compose(self):
        yield Vertical(
            Label(Text.from_markup(f"[b green]Textual `ls` App[/b green]"), id="input_title"),
        )

class LsOutput(Container):
    def compose(self):
        yield Label("Enter a directory and push the button")

    def run_ls(self, directory):
        if directory and os.path.exists(directory):
            entries = os.listdir(directory)
        else:
            entries = ["Invalid directory"]

        # Add new labels to the container
        for entry in entries:
            self.mount(Label(entry))


class LsApp(App):
    CSS_PATH="Ls.tcss"
    output = ''

    def __init__(self):
        super().__init__()
        self.ls_header = LsHeader()
        self.ls_form = LsForm()
        self.ls_output = LsOutput()

    def compose(self):
        yield Vertical(
            self.ls_header,
            self.ls_form,
            self.ls_output,
            id="ls_app"
        )

    def on_target_directory(self, message):
        self.ls_output.run_ls(message.directory)
        print(f"on_target(): {message.directory}")


if __name__ == "__main__":
    app = LsApp()
    app.run()