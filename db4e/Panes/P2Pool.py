"""
db4e/Panes/P2Pool.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.containers import Container, ScrollableContainer, Vertical
from textual.widgets import Label, Input, Button, MarkdownViewer

from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Constants.Fields import (
    FORM_INTRO_FIELD, PANE_BOX_FIELD, FORM_1_FIELD
)
from db4e.Constants.Labels import (
    INSTANCE_LABEL, IP_ADDR_LABEL, P2POOL_LABEL, P2POOL_REMOTE_LABEL, 
    PROCEED_LABEL, STRATUM_PORT_LABEL
)
from db4e.Constants.Defaults import (
    STRATUM_PORT_DEFAULT
)

class P2Pool(Container):

    instance_input = Input(id="instance_input", restrict=f"[a-zA-Z0-9_\-]*", compact=True)
    ip_addr_input = Input(id="ip_addr_input", restrict=f"[a-z0-9._\-]*", compact=True)
    stratum_port_input = Input(id="stratum_port_input", restrict=f"[0-9]*", compact=True)
    remote_flag = bool

    def compose(self):

        # Local P2Pool daemon deployment form
        INTRO = "This screen provides a form for creating a new " \
            f"[bold cyan]{P2POOL_LABEL}[/] deployment."

        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=FORM_INTRO_FIELD),

                Vertical(
                    Label('🚧 [cyan]Coming Soon[/] 🚧'),
                    classes=FORM_1_FIELD)),
                classes=PANE_BOX_FIELD)

    def reset_data(self):
        self.instance_input.value = ""
        self.ip_addr_input.value = ""
        self.stratum_port_input.value = str(STRATUM_PORT_DEFAULT)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        pass
        #self.app.post_message(Db4eMsg(self, form_data=form_data))