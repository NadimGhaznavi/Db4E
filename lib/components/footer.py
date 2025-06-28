"""lib/components/footer.py"""
from textual.widgets import Footer, Button
from textual.reactive import reactive
from textual.containers import Horizontal

class Db4eFooter(Footer):
    context = reactive("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.button_container = Horizontal()
        self.mount(self.button_container)

    def watch_context(self, old_context, new_context):
        self.update_buttons(new_context)

    def update_buttons(self, context: str):
        self.button_container.clear()
        if context == "Deployments":
            self.button_container.mount(Button("^N New Deployment", id="new"))
        elif context.startswith("Deployments/"):
            self.button_container.mount(Button("Update", id="update"))
            self.button_container.mount(Button("Enable/Disable", id="toggle"))
            self.button_container.mount(Button("Delete", id="delete"))
        else:
            self.button_container.mount(Button("View", id="view"))