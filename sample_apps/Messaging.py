from textual.app import App, ComposeResult
from textual.widgets import Button
from textual.containers import Container
from textual.message import Message

class SubmitForm(Message):
    def __init__(self, form_data: dict) -> None:
        super().__init__()
        self.form_data = form_data
        print("Built the message")

class InitialSetup(Container):
    def compose(self) -> ComposeResult:
        yield Button("Submit")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        print("Button clicked")
        self.app.post_message(SubmitForm({"foo": "bar"}))

class MyApp(App):
    def compose(self) -> ComposeResult:
        yield InitialSetup()

    async def on_submit_form(self, message: SubmitForm) -> None:
        print("Got the memo!")

    async def on_message(self, message: Message) -> None:
        print(f"Got ALL the memos: {message}")

if __name__ == "__main__":
    MyApp().run()
