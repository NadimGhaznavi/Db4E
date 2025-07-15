from textual.app import App
from textual.widgets import Label, RadioButton, RadioSet, Button, Input
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive

class MyForm(Container):
    radio_button_list = reactive(list, always_update=True)
    radio_set = RadioSet(id="radio_set_input")

    def compose(self):
        yield Horizontal(Label("Radio Set"), id="radio_set_box")
        yield self.radio_set

    def watch_radio_button_list(self, old, new):
        rs = self.radio_set
        for child in list(rs.children):
            child.remove()
        for idx, label in enumerate(new):
            rb = RadioButton(label)
            rs.mount(rb)
            if idx == 0:
                rb.value = True

    def add_radio_button(self, label):
        self.radio_button_list = [*self.radio_button_list, label]

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
        height: 1fr;
    }
    #radio_set_box {
        border: round;
        height: auto;
    }
    #new_radio_button_box {
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
    my_new_radio_button = Input(id="new_radio_button_label", compact=True)

    def compose(self):
        yield Vertical(
            Horizontal(
                self.my_form, 
                id="form_box"),
            Horizontal(
                Label("New Radio Button"),
                self.my_new_radio_button, 
                id="new_radio_button_box"),
            Horizontal(self.my_button, id="button_box")
        )

    def on_button_pressed(self, event):
        new_button_label = self.query_one("#new_radio_button_label", Input).value
        self.my_form.add_radio_button(new_button_label)
    

if __name__ == "__main__":
    app = ReactiveApp()
    app.run()