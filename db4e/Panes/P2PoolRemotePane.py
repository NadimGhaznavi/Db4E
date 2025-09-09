"""
db4e/Panes/P2PoolRemotePane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Label, Button, Input

from db4e.Modules.P2PoolRemote import P2PoolRemote
from db4e.Modules.Helper import gen_results_table
from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Messages.RefreshNavPane import RefreshNavPane
from db4e.Constants.Labels import DLabel
from db4e.Constants.Form import Form
from db4e.Constants.Fields import (
    ADD_DEPLOYMENT_FIELD, OP_FIELD, NEW_FIELD, UPDATE_FIELD,
    ELEMENT_FIELD, TO_METHOD_FIELD, TO_MODULE_FIELD)
from db4e.Constants.Fields import DMod, DField, DElem
from db4e.Constants.Buttons import (
    DELETE_BUTTON_FIELD, NEW_BUTTON_FIELD, BUTTON_ROW_FIELD, UPDATE_BUTTON_FIELD)
from db4e.Constants.Jobs import DJob



class P2PoolRemotePane(Container):

    instance_label = Label("", id="instance_label",classes=Form.STATIC)
    instance_input = Input(
        id="instance_input", restrict=f"[a-zA-Z0-9_\-]*", compact=True, 
        classes=Form.INPUT_30)
    ip_addr_input = Input(
        id="ip_addr_input", restrict=f"[a-z0-9._\-]*", compact=True,
        classes=Form.INPUT_30)
    stratum_port_input = Input(
        id="stratum_port_input", restrict=f"[0-9]*", compact=True, 
        classes=Form.INPUT_30)
    health_msgs = Label()
    delete_button = Button(label=DLabel.DELETE, id=DELETE_BUTTON_FIELD)
    new_button = Button(label=DLabel.NEW, id=NEW_BUTTON_FIELD)
    update_button = Button(label=DLabel.UPDATE, id=UPDATE_BUTTON_FIELD)


    def compose(self):
        # Remote P2Pool deployment form
        INTRO = f"View and edit the deployment settings for the " \
            f"[cyan]{DLabel.P2POOL_REMOTE}[/] deployment here."

        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=Form.INTRO),

                Vertical(
                    Horizontal(
                        Label(DLabel.INSTANCE, classes=Form.FORM_LABEL),
                        self.instance_input, self.instance_label),
                    Horizontal(
                        Label(DLabel.IP_ADDR, classes=Form.FORM_LABEL),
                        self.ip_addr_input),
                    Horizontal(
                        Label(DLabel.STRATUM_PORT, classes=Form.FORM_LABEL),
                        self.stratum_port_input),
                    classes=Form.FORM_3),

                Vertical(
                    self.health_msgs,
                    classes=Form.HEALTH_BOX,
                ),

                Horizontal(
                    self.new_button,
                    self.update_button,
                    self.delete_button,
                    classes=BUTTON_ROW_FIELD
                ),
        
                classes=Form.PANE_BOX))


    def set_data(self, p2pool: P2PoolRemote):
        self.instance_input.value = p2pool.instance()
        self.instance_label.update(p2pool.instance())
        self.ip_addr_input.value = p2pool.ip_addr()
        self.stratum_port_input.value = str(p2pool.stratum_port())
        self.health_msgs.update(gen_results_table(p2pool.pop_msgs()))
        self.p2pool = p2pool
        # Set update button or new button visibility, using the .tcss definitions
        if p2pool.instance():
            # This is an update operation
            self.remove_class(NEW_FIELD)
            self.add_class(UPDATE_FIELD)

        else:
            # This is a new operation
            self.remove_class(UPDATE_FIELD)
            self.add_class(NEW_FIELD)
        

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        self.p2pool.instance(self.query_one("#instance_input", Input).value)
        self.p2pool.ip_addr(self.query_one("#ip_addr_input", Input).value)
        self.p2pool.stratum_port(self.query_one("#stratum_port_input", Input).value)


        if button_id == NEW_BUTTON_FIELD:
            # No original instance, this is a new deployment
            form_data = {
                TO_MODULE_FIELD: DMod.OPS_MGR,
                TO_METHOD_FIELD: ADD_DEPLOYMENT_FIELD,
                DField.ELEMENT_TYPE: DElem.P2POOL_REMOTE,
                ELEMENT_FIELD: self.p2pool,
            }

        elif button_id == UPDATE_BUTTON_FIELD:
            # There was an original instance, so this is an update            
            form_data = {
                TO_MODULE_FIELD: DMod.DEPLOYMENT_MGR,
                TO_METHOD_FIELD: DJob.POST_JOB,
                OP_FIELD: DJob.UPDATE,
                DField.ELEMENT_TYPE: DElem.P2POOL_REMOTE,
                ELEMENT_FIELD: self.p2pool,
            }

        elif button_id == DELETE_BUTTON_FIELD:
            form_data = {
                TO_MODULE_FIELD: DMod.DEPLOYMENT_MGR,
                TO_METHOD_FIELD: DJob.POST_JOB,
                OP_FIELD: DJob.DELETE,
                DField.ELEMENT_TYPE: DElem.P2POOL_REMOTE,
                ELEMENT_FIELD: self.p2pool,
            }
            
        self.app.post_message(Db4eMsg(self, form_data=form_data))
        