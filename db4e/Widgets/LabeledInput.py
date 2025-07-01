# db4e/Widgets/LabeledInput.py
from textual.widget import Widget
from textual.widgets import Input, Label
from textual.containers import Horizontal, Vertical
from textual.app import ComposeResult
from textual.message import Message

class LabeledInput(Widget):

    class Changed(Message):
        def __init__(self, sender: "LabeledInput", value: str) -> None:
            self.value = value
            super().__init__(sender)

    def __init__(
        self,
        label: str = "",
        placeholder: str = "",
        value: str = "",
        *,
        id: str | None = None,
        classes: str | None = None,
    ):
        super().__init__(id=id, classes=classes)
        self.label_text = label
        self.placeholder = placeholder
        self.value = value

    def compose(self) -> ComposeResult:
        yield Label(self.label_text, id="input_label")
        yield Input(value=self.value, placeholder=self.placeholder, id="input_field")

    async def on_input_changed(self, event: Input.Changed) -> None:
        # Forward the changed message with the current input value
        await self.post_message(self.Changed(self, event.value))
