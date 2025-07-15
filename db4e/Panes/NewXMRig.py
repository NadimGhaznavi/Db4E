"""
db4e/Panes/NewXMRig.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""

from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Label, Input, Button, MarkdownViewer, RadioSet, RadioButton, Static)

from db4e.Modules.DeploymentMgr import DeploymentMgr

from db4e.Messages.SubmitFormData import SubmitFormData
from db4e.Constants.Fields import (
    ADD_DEPLOYMENT_FIELD, COMPONENT_FIELD, DEPLOYMENT_MGR_FIELD, INSTANCE_FIELD, 
    NUM_THREADS_FIELD, P2POOL_FIELD, P2POOL_ID_FIELD, REMOTE_FIELD, 
    TO_MODULE_FIELD, TO_METHOD_FIELD, XMRIG_FIELD
)
from db4e.Constants.Labels import (
    INSTANCE_LABEL, P2POOL_LABEL, PROCEED_LABEL, NUM_THREADS_LABEL, XMRIG_LABEL
)
from db4e.Constants.Defaults import (
    STRATUM_PORT_DEFAULT
)

class NewXMRig(Container):

    p_dict = {}
    instance_input = Input(id="instance_input", restrict=f"[a-zA-Z0-9_\-]*", compact=True)
    num_threads_input = Input(id="num_threads_input", restrict=f"[0-9]*", compact=True)
    radio_set = RadioSet(id="radio_set")

    def compose(self):
        # Remote P2Pool daemon deployment form
        STATIC_CONTENT = "This screen provides a form for creating a new "
        STATIC_CONTENT += f"{XMRIG_LABEL} deployment. The 'number of threads' determines how "
        STATIC_CONTENT += "man CPU threads are allocated to the XMRig miner. XMRig connects to a "
        STATIC_CONTENT += "P2Pool deployment, which in turn connects to a Monero daemon "
        STATIC_CONTENT += "deployment."

        yield Vertical(
            MarkdownViewer(STATIC_CONTENT, show_table_of_contents=False, classes="form_intro"),

            Vertical(
                Horizontal(
                    Label(INSTANCE_LABEL, id="instance_label"),
                    self.instance_input),
                Horizontal(
                    Label(NUM_THREADS_LABEL, id="num_threads_label"),
                    self.num_threads_input),
                id="xmrig_edit_form"),

            Vertical(
                Label("P2Pool Deployment", id="p2pool_label"),
                self.radio_set, 
                id="radio_set_box"),

            Horizontal(
                Button(label=PROCEED_LABEL, id="proceed_button"),
                id="buttons"),
            
        id="pane")

    def get_p2pool_id(self, instance=None):
        return self.p_dict[instance] if instance else None

    def get_p2pool_instances(self):
        return self.p_dict

    def reset_data(self):
        self.instance_input.value = ""
        self.num_threads_input.value = ""

    def set_p2pool_instances(self, p_dict):
        self.p_dict = p_dict
        self.refresh()

    def set_data(self, rec):
        p_dict = {}
        p_elems = []
        for (instance, id) in rec[P2POOL_FIELD]:
            p_dict[instance] = id
            p_elems.append(instance)
        self.set_p2pool_instances(p_dict)
        self.radio_set.remove_children()
        for instance in p_dict.keys():
            self.radio_set.mount(RadioButton(instance))
        self.refresh()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        radio_set = self.query_one("#radio_set", RadioSet)
        is_radiobutton = radio_set.pressed_button
        p2pool_instance = None
        if is_radiobutton:
            p2pool_instance = radio_set.pressed_button.label
        p2pool_id = self.get_p2pool_id(p2pool_instance)
        form_data = {
            COMPONENT_FIELD: XMRIG_FIELD,
            TO_MODULE_FIELD: DEPLOYMENT_MGR_FIELD,
            TO_METHOD_FIELD: ADD_DEPLOYMENT_FIELD,
            REMOTE_FIELD: False,
            INSTANCE_FIELD: self.query_one("#instance_input", Input).value,
            NUM_THREADS_FIELD: self.query_one("#num_threads_input", Input).value,
            P2POOL_ID_FIELD: p2pool_id
        }
        self.app.post_message(SubmitFormData(self, form_data=form_data))
