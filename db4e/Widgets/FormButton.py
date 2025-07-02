# db4e/Widgets/ThemedButton.py
from textual.widget import Widget
from textual.widgets import Button
from textual.message import Message
from textual.app import ComposeResult

class FormButton(Widget):

    class Pressed(Message):
        def __init__(self, sender: "FormButton") -> None:
            super().__init__(sender) 

    def __init__(self, label: str, *, id: str, classes: str | None = None):
        super().__init__(id=id, classes=classes)
        self.label = label

    def compose(self) -> ComposeResult:
        yield Button(self.label, id=self.id, compact=True)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        await self.post_message(self.Pressed(self))