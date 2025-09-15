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
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DField import DField
from db4e.Constants.DElem import DElem
from db4e.Constants.DModule import DModule
from db4e.Constants.DMethod import DMethod
from db4e.Constants.DJob import DJob
from db4e.Constants.DButton import DButton
from db4e.Constants.DForm import DForm


class P2PoolRemotePane(Container):

    instance_label = Label("", id="instance_label",classes=DForm.STATIC)
    instance_input = Input(
        id="instance_input", restrict=f"[a-zA-Z0-9_\-]*", compact=True, 
        classes=DForm.INPUT_30)
    ip_addr_input = Input(
        id="ip_addr_input", restrict=f"[a-z0-9._\-]*", compact=True,
        classes=DForm.INPUT_30)
    stratum_port_input = Input(
        id="stratum_port_input", restrict=f"[0-9]*", compact=True, 
        classes=DForm.INPUT_30)
    health_msgs = Label()
    delete_button = Button(label=DLabel.DELETE, id=DButton.DELETE)
    new_button = Button(label=DLabel.NEW, id=DButton.NEW)
    update_button = Button(label=DLabel.UPDATE, id=DButton.UPDATE)


    def compose(self):
        # Remote P2Pool deployment form
        INTRO = f"View and edit the deployment settings for the " \
            f"[cyan]{DLabel.P2POOL_REMOTE}[/] deployment here."

        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=DForm.INTRO),

                Vertical(
                    Horizontal(
                        Label(DLabel.INSTANCE, classes=DForm.FORM_LABEL),
                        self.instance_input, self.instance_label),
                    Horizontal(
                        Label(DLabel.IP_ADDR, classes=DForm.FORM_LABEL),
                        self.ip_addr_input),
                    Horizontal(
                        Label(DLabel.STRATUM_PORT, classes=DForm.FORM_LABEL),
                        self.stratum_port_input),
                    classes=DForm.FORM_3),

                Vertical(
                    self.health_msgs,
                    classes=DForm.HEALTH_BOX,
                ),

                Horizontal(
                    self.new_button,
                    self.update_button,
                    self.delete_button,
                    classes=DForm.BUTTON_ROW
                ),
        
                classes=DForm.PANE_BOX))


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
            self.remove_class(DField.NEW)
            self.add_class(DField.UPDATE)

        else:
            # This is a new operation
            self.remove_class(DField.UPDATE)
            self.add_class(DField.NEW)
        

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        self.p2pool.instance(self.query_one("#instance_input", Input).value)
        self.p2pool.ip_addr(self.query_one("#ip_addr_input", Input).value)
        self.p2pool.stratum_port(self.query_one("#stratum_port_input", Input).value)


        if button_id == DButton.NEW:
            # No original instance, this is a new deployment
            form_data = {
                DField.TO_MODULE: DModule.OPS_MGR,
                DField.TO_METHOD: DMethod.ADD_DEPLOYMENT,
                DField.ELEMENT_TYPE: DElem.P2POOL_REMOTE,
                DField.ELEMENT: self.p2pool,
            }

        elif button_id == DButton.UPDATE:
            # There was an original instance, so this is an update            
            form_data = {
                DField.TO_MODULE: DModule.DEPLOYMENT_CLIENT,
                DField.TO_METHOD: DMethod.UPDATE_DEPLOYMENT,
                DField.ELEMENT_TYPE: DElem.P2POOL_REMOTE,
                DField.ELEMENT: self.p2pool,
            }

        elif button_id == DButton.DELETE:
            form_data = {
                DField.TO_MODULE: DModule.DEPLOYMENT_CLIENT,
                DField.TO_METHOD: DMethod.DELETE_DEPLOYMENT,
                DField.ELEMENT_TYPE: DElem.P2POOL_REMOTE,
                DField.ELEMENT: self.p2pool,
            }
            
        self.app.post_message(Db4eMsg(self, form_data=form_data))
        