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
from db4e.Constants.Fields import (
    ADD_DEPLOYMENT_FIELD, 
    FORM_3_FIELD, NEW_FIELD, ELEMENT_TYPE_FIELD, INSTANCE_FIELD,
    FORM_INPUT_30_FIELD, FORM_INTRO_FIELD, FORM_LABEL_FIELD,
    HEALTH_BOX_FIELD, ELEMENT_FIELD, OPS_MGR_FIELD, PANE_BOX_FIELD, P2POOL_REMOTE_FIELD,
    TO_METHOD_FIELD, TO_MODULE_FIELD)
from db4e.Constants.Labels import (
    INSTANCE_LABEL, IP_ADDR_LABEL,
    P2POOL_REMOTE_LABEL, STRATUM_PORT_LABEL)
from db4e.Constants.Buttons import (
    DELETE_BUTTON_FIELD, NEW_BUTTON_FIELD, BUTTON_ROW_FIELD, UPDATE_BUTTON_FIELD, 
    DELETE_LABEL, UPDATE_LABEL, NEW_LABEL)
from db4e.Constants.Jobs import (
    JOB_QUEUE_FIELD, POST_JOB_FIELD, OP_FIELD, DELETE_FIELD, UPDATE_FIELD)



class P2PoolRemotePane(Container):

    instance_input = Input(
        id="instance_input", restrict=f"[a-zA-Z0-9_\-]*", compact=True, 
        classes=FORM_INPUT_30_FIELD)
    ip_addr_input = Input(
        id="ip_addr_input", restrict=f"[a-z0-9._\-]*", compact=True,
        classes=FORM_INPUT_30_FIELD)
    stratum_port_input = Input(
        id="stratum_port_input", restrict=f"[0-9]*", compact=True, 
        classes=FORM_INPUT_30_FIELD)
    health_msgs = Label()
    delete_button = Button(label=DELETE_LABEL, id=DELETE_BUTTON_FIELD)
    new_button = Button(label=NEW_LABEL, id=NEW_BUTTON_FIELD)
    update_button = Button(label=UPDATE_LABEL, id=UPDATE_BUTTON_FIELD)


    def compose(self):
        # Remote P2Pool deployment form
        INTRO = f"View and edit the deployment settings for the " \
            f"[cyan]{P2POOL_REMOTE_LABEL}[/] deployment here."

        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=FORM_INTRO_FIELD),

                Vertical(
                    Horizontal(
                        Label(INSTANCE_LABEL, classes=FORM_LABEL_FIELD),
                        self.instance_input),
                    Horizontal(
                        Label(IP_ADDR_LABEL, classes=FORM_LABEL_FIELD),
                        self.ip_addr_input),
                    Horizontal(
                        Label(STRATUM_PORT_LABEL, classes=FORM_LABEL_FIELD),
                        self.stratum_port_input),
                    classes=FORM_3_FIELD),

                Vertical(
                    self.health_msgs,
                    classes=HEALTH_BOX_FIELD,
                ),

                Horizontal(
                    self.new_button,
                    self.update_button,
                    self.delete_button,
                    classes=BUTTON_ROW_FIELD
                ),
        
                classes=PANE_BOX_FIELD))


    def set_data(self, p2pool: P2PoolRemote):
        self.instance_input.value = p2pool.instance()
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
                TO_MODULE_FIELD: OPS_MGR_FIELD,
                TO_METHOD_FIELD: ADD_DEPLOYMENT_FIELD,
                ELEMENT_TYPE_FIELD: P2POOL_REMOTE_FIELD,
                ELEMENT_FIELD: self.p2pool,
            }

        elif button_id == UPDATE_BUTTON_FIELD:
            # There was an original instance, so this is an update            
            form_data = {
                TO_MODULE_FIELD: JOB_QUEUE_FIELD,
                TO_METHOD_FIELD: POST_JOB_FIELD,
                OP_FIELD: UPDATE_FIELD,
                ELEMENT_TYPE_FIELD: P2POOL_REMOTE_FIELD,
                ELEMENT_FIELD: self.p2pool,
                INSTANCE_FIELD: self.p2pool.instance(),
            }

        elif button_id == DELETE_BUTTON_FIELD:
            form_data = {
                TO_MODULE_FIELD: JOB_QUEUE_FIELD,
                TO_METHOD_FIELD: POST_JOB_FIELD,
                OP_FIELD: DELETE_FIELD,
                ELEMENT_TYPE_FIELD: P2POOL_REMOTE_FIELD,
                INSTANCE_FIELD: self.p2pool.instance(),
            }
            
        else:
            raise ValueError(f"No handler for {button_id}")
        self.app.post_message(Db4eMsg(self, form_data=form_data))
        