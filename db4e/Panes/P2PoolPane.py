"""
db4e/Panes/P2PoolPane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.containers import Container, ScrollableContainer, Vertical, Horizontal
from textual.widgets import Label, Input, Button, MarkdownViewer, RadioButton, RadioSet

from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Modules.P2Pool import P2Pool
from db4e.Modules.Helper import gen_results_table
from db4e.Constants.Fields import (
    FORM_INTRO_FIELD, PANE_BOX_FIELD, FORM_LABEL_FIELD, FORM_INPUT_30_FIELD,
    STATIC_CONTENT_FIELD, FORM_2_FIELD, HEALTH_BOX_FIELD, RADIO_SET_FIELD, 
    FORM_5_FIELD, NEW_FIELD, DISABLE_FIELD, ENABLE_FIELD)
from db4e.Constants.Labels import (
    INSTANCE_LABEL, P2POOL_LABEL, 
    STRATUM_PORT_LABEL, CONFIG_LABEL, IN_PEERS_LABEL, OUT_PEERS_LABEL,
    LOG_LEVEL_LABEL, P2P_BIND_PORT_LABEL, STRATUM_PORT_LABEL)
from db4e.Constants.Buttons import (
    DELETE_BUTTON_FIELD, NEW_BUTTON_FIELD, BUTTON_ROW_FIELD, UPDATE_BUTTON_FIELD, 
    DELETE_LABEL, UPDATE_LABEL, NEW_LABEL, ENABLE_BUTTON_FIELD, ENABLE_LABEL,
    DISABLE_BUTTON_FIELD, DISABLE_LABEL)
from db4e.Constants.Jobs import (
    JOB_QUEUE_FIELD, POST_JOB_FIELD, OP_FIELD, DELETE_FIELD, UPDATE_FIELD)


class P2PoolPane(Container):

    instance_input = Input(
        id="instance_input", restrict=f"[a-zA-Z0-9_\-]*", compact=True,
        classes=FORM_INPUT_30_FIELD)
    config_label = Label("", classes=STATIC_CONTENT_FIELD)
    chain_radio_set = RadioSet(id="chain_radio_set", classes=RADIO_SET_FIELD)
    in_peers_input = Input(
        id="in_peers_input", restrict=f"[0-9]*", compact=True,
        classes=FORM_INPUT_30_FIELD)
    out_peers_input = Input(
        id="out_peers_input", restrict=f"[0-9]*", compact=True,
        classes=FORM_INPUT_30_FIELD)
    log_level_input = Input(
        id="log_level_input", restrict=f"[0-9]*", compact=True,
        classes=FORM_INPUT_30_FIELD)
    p2p_bind_port_input = Input(
        id="p2p_bind_port_input", restrict=f"[0-9]*", compact=True,
        classes=FORM_INPUT_30_FIELD)
    stratum_port_input = Input(
        id="stratum_port_input", restrict=f"[0-9]*", compact=True,
        classes=FORM_INPUT_30_FIELD)
    radio_set = RadioSet(id="radio_set", classes=RADIO_SET_FIELD)

    health_msgs = Label()

    delete_button = Button(label=DELETE_LABEL, id=DELETE_BUTTON_FIELD)
    disable_button = Button(label=DISABLE_LABEL, id=DISABLE_BUTTON_FIELD)
    enable_button = Button(label=ENABLE_LABEL, id=ENABLE_BUTTON_FIELD)
    new_button = Button(label=NEW_LABEL, id=NEW_BUTTON_FIELD)
    update_button = Button(label=UPDATE_LABEL, id=UPDATE_BUTTON_FIELD)
    p2pool = None


    def compose(self):

        # Local P2Pool daemon deployment form
        INTRO = "This screen provides a form for creating a new " \
            f"[bold cyan]{P2POOL_LABEL}[/] deployment."

        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=FORM_INTRO_FIELD),

                Vertical(
                    Horizontal(
                        Label(CONFIG_LABEL, classes=FORM_LABEL_FIELD),
                        self.config_label),
                    Horizontal(
                        Label(INSTANCE_LABEL, classes=FORM_LABEL_FIELD),
                        self.instance_input),
                    classes=FORM_2_FIELD),

                Vertical(
                    self.chain_radio_set),

                Vertical(
                    Horizontal(
                        Label(IN_PEERS_LABEL, classes=FORM_LABEL_FIELD),
                        self.in_peers_input),
                    Horizontal(
                        Label(OUT_PEERS_LABEL, classes=FORM_LABEL_FIELD),
                        self.out_peers_input),
                    Horizontal(
                        Label(P2P_BIND_PORT_LABEL, classes=FORM_LABEL_FIELD),
                        self.p2p_bind_port_input),
                    Horizontal(
                        Label(STRATUM_PORT_LABEL, classes=FORM_LABEL_FIELD),
                        self.stratum_port_input),
                    Horizontal(
                        Label(LOG_LEVEL_LABEL, classes=FORM_LABEL_FIELD),
                        self.log_level_input),
                    classes=FORM_5_FIELD),
                    
                Vertical(
                    self.radio_set),

                Vertical(
                    self.health_msgs,
                    classes=HEALTH_BOX_FIELD,
                ),

                Vertical(
                    Horizontal(
                        self.new_button,
                        self.update_button,
                        self.enable_button,
                        self.disable_button,
                        self.delete_button,
                        classes=BUTTON_ROW_FIELD))),
                
            classes=PANE_BOX_FIELD)


    def set_data(self, p2pool: P2Pool):
        self.p2pool = p2pool
        self.instance_input.value = p2pool.instance()
        self.config_label.update(p2pool.config_file())
        self.in_peers_input.value = str(p2pool.in_peers())
        self.out_peers_input.value = str(p2pool.out_peers())
        self.p2p_bind_port_input.value = str(p2pool.p2p_bind_port())
        self.stratum_port_input.value = str(p2pool.stratum_port())
        self.log_level_input.value = str(p2pool.log_level())

        # Configure button visibility
        if p2pool.instance():
            # This is an update operation
            self.remove_class(NEW_FIELD)
            self.add_class(UPDATE_FIELD)

            if p2pool.enabled():
                self.remove_class(DISABLE_FIELD)
                self.add_class(ENABLE_FIELD)
            else:
                self.remove_class(ENABLE_FIELD)
                self.add_class(DISABLE_FIELD)
        else:
            # This is a new operation
            self.remove_class(UPDATE_FIELD)
            self.add_class(NEW_FIELD)

        self.health_msgs.update(gen_results_table(p2pool.pop_msgs()))                    

    def on_button_pressed(self, event: Button.Pressed) -> None:
        pass
        #self.app.post_message(Db4eMsg(self, form_data=form_data))