"""
db4e/Panes/XMRig.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
    License: GPL 3.0
"""
import time
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Label, MarkdownViewer, Button, Input, RadioSet, RadioButton

from db4e.Messages.SubmitFormData import SubmitFormData
from db4e.Constants.Fields import (
    COMPONENT_FIELD, DEPLOYMENT_MGR_FIELD,  
    INSTANCE_FIELD, NUM_THREADS_FIELD, ORIG_INSTANCE_FIELD, 
    P2POOL_FIELD, P2POOL_ID_FIELD, RADIO_MAP, RADIO_SET,
    REMOTE_FIELD, TO_MODULE_FIELD, TO_METHOD_FIELD, 
    UPDATE_DEPLOYMENT_FIELD, XMRIG_FIELD
)
from db4e.Constants.Labels import (
    DELETE_LABEL, INSTANCE_LABEL, NUM_THREADS_LABEL, UPDATE_LABEL, XMRIG_LABEL
)


class XMRig(Container):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._p_dict = {}

    def get_p2pool_id(self, instance=None):
        return self._p_dict[instance]

    def set_p2pool_instances(self, p_dict):
        self._p_dict = p_dict
        #self.refresh(recompose=True)

    def set_data(self, rec):
        num_threads = rec[NUM_THREADS_FIELD]
        instance = rec[INSTANCE_FIELD]
        orig_instance = instance
        radio_set = rec[RADIO_SET]

        self.set_p2pool_instances(rec[RADIO_MAP])

        STATIC_CONTENT = f"This screen allows you to view and edit the deployment "
        STATIC_CONTENT += f"settings for the {XMRIG_LABEL} deployment."
        md = Vertical(
            MarkdownViewer(STATIC_CONTENT, show_table_of_contents=False, classes="form_intro"),

            Vertical(
                Horizontal(
                    Label(INSTANCE_LABEL, id="xmrig_instance_label"),
                    Input(id="xmrig_instance_input",
                          restrict=f"[a-zA-Z0-9_\-]*", value=instance, compact=True)),
                Horizontal(
                    Label(NUM_THREADS_LABEL, id="xmrig_num_threads_label"),
                    Input(id="num_threads_input",
                          restrict=f"[a-z0-9._\-]*", value=num_threads, compact=True)),
                id="xmrig_form"),

            Vertical(
                Label("P2Pool Deployment", id="xmrig_p2pool_label"),
                radio_set, 
                id="xmrig_p2pool_box"),

            Input(id="xmrig_orig_instance", value=orig_instance, classes="hidden"),

            Horizontal(
                Button(label=UPDATE_LABEL, id="xmrig_update_button"),
                Button(label=DELETE_LABEL, id="xmrig_delete_button")
            ),
        id="xmrig_pane")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        radio_set = self.query_one("#xmrig_p2pool_radioset", RadioSet)
        p2pool_instance = radio_set.pressed_button.label
        p2pool_id = self.get_p2pool_id(p2pool_instance)
        form_data = {
            COMPONENT_FIELD: XMRIG_FIELD,
            TO_MODULE_FIELD: DEPLOYMENT_MGR_FIELD,
            TO_METHOD_FIELD: UPDATE_DEPLOYMENT_FIELD,
            REMOTE_FIELD: False,
            INSTANCE_FIELD: self.query_one("#xmrig_instance_input", Input).value,
            NUM_THREADS_FIELD: self.query_one("#xmrig_num_threads_input", Input).value,
            ORIG_INSTANCE_FIELD: self.query_one("#xmrig_orig_instance", Input).value,
            P2POOL_ID_FIELD: p2pool_id
        }
        self.app.post_message(SubmitFormData(self, form_data=form_data))
