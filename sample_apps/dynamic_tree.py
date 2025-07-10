from textual.app import App, ComposeResult
from textual.widgets import Button, Tree
from textual.containers import Container
from textual.message import Message


class UpdateNavMsg(Message):
    def __init__(self):
        super().__init__()

class NavTree(Container):

    def __init__(self):
        super().__init__()
        self.nav_tree = Tree("The Root")

    def compose(self):
        yield self.nav_tree

    def add_leaf(self):
        self.nav_tree.root.add_leaf("New Leaf")

class MyApp(App):

    def __init__(self):
        super().__init__()
        self.nav_tree = NavTree()

    def compose(self) -> ComposeResult:
        yield self.nav_tree
        yield Button(label="Add Leaf")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        self.nav_tree.add_leaf()

if __name__ == "__main__":
    MyApp().run()
