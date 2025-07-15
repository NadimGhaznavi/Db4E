from textual.app import App
from textual.widgets import Label, Input, Button
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive

class MyForm(Container):

    default_value = reactive("Not Set")
    input_widget = Input(id="field_input", compact=True)

    def compose(self):
        yield Horizontal(
            Label("Input Field"),
            self.input_widget,
        )

    def set_value(self, value):
        self.default_value = value

    def watch_default_value(self):
        self.input_widget.value = self.default_value


class ReactiveApp(App):

    DEFAULT_CSS = """
    #form_fields_box {
        border: round;
    }
    Label {
        padding: 0 2;
        align: center middle;
    }
    #field_input {
        width: 10;
    }
    #form_box {
        border: round;
        height: 3;
    }
    #button_box {
        border: round;
        height: 3;
        width: auto;
    }

    """

    my_form = MyForm()
    my_button = Button("Update", id="my_button", compact=True)

    def compose(self):
        yield Vertical(
            Horizontal(self.my_form, id="form_box"),
            Horizontal(self.my_button, id="button_box")
        )

    def set_value(self, value):
        self.my_form.set_value(value)

    def on_button_pressed(self, event):
        self.my_form.set_value("Updated")
    

if __name__ == "__main__":
    app = ReactiveApp()
    app.run()