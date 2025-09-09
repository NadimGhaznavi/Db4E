"""
db4e/Panes/XMRigPane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.reactive import reactive
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Label, Input, Button, RadioSet, RadioButton)

from db4e.Modules.Helper import gen_results_table
from db4e.Modules.XMRig import XMRig
from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Messages.RefreshNavPane import RefreshNavPane
from db4e.Constants.Buttons import(
    BUTTON_ROW_FIELD, DELETE_BUTTON_FIELD, ENABLE_BUTTON_FIELD, 
    DISABLE_BUTTON_FIELD, 
    UPDATE_BUTTON_FIELD, NEW_BUTTON_FIELD)
from db4e.Constants.Fields import (
    ADD_DEPLOYMENT_FIELD, ELEMENT_FIELD, UPDATE_FIELD,
    ENABLE_FIELD, OP_FIELD,
    RADIO_BUTTON_TYPE_FIELD, RADIO_SET_FIELD,
    TO_METHOD_FIELD, TO_MODULE_FIELD, DISABLE_FIELD, NEW_FIELD)
from db4e.Constants.Fields import DMod, DElem, DField
from db4e.Constants.Jobs import DJob
from db4e.Constants.Labels import DLabel
from db4e.Constants.Form import Form


class XMRigPane(Container):

    instance_label = Label("", id="instance_label",classes=Form.STATIC)
    radio_button_list = reactive([], always_update=True)
    radio_set = RadioSet(id="radio_set", classes=RADIO_SET_FIELD)
    instance_map = {}
    
    config_label = Label("", classes=Form.STATIC)
    instance_input = Input(
        id="instance_input", restrict=f"[a-zA-Z0-9_\-]*", compact=True,
        classes=Form.INPUT_15)
    num_threads_input = Input(
        id="num_threads_input", restrict=f"[0-9]*", compact=True,
        classes=Form.INPUT_15)
    
    health_msgs = Label()

    delete_button = Button(label=DLabel.DELETE, id=DELETE_BUTTON_FIELD)
    disable_button = Button(label=DLabel.DISABLE, id=DISABLE_BUTTON_FIELD)
    enable_button = Button(label=DLabel.ENABLE, id=ENABLE_BUTTON_FIELD)
    new_button = Button(label=DLabel.NEW, id=NEW_BUTTON_FIELD)
    update_button = Button(label=DLabel.UPDATE, id=UPDATE_BUTTON_FIELD)
    xmrig = None


    def compose(self):
        # Remote P2Pool daemon deployment form
        INTRO = f"View and edit the deployment settings for the " \
            f"[cyan]{DLabel.XMRIG}[/] deployment here."


        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=Form.INTRO),

                Vertical(
                    Horizontal(
                        Label(DLabel.INSTANCE, classes=Form.FORM_LABEL),
                        self.instance_input, self.instance_label),
                    Horizontal(
                        Label(DLabel.NUM_THREADS, classes=Form.FORM_LABEL),
                        self.num_threads_input),
                    Horizontal(
                        Label(DLabel.CONFIG_FILE, classes=Form.FORM_LABEL),
                        self.config_label),
                    classes=Form.FORM_3, id="form_field"),

                Vertical(
                    self.radio_set),

                Vertical(
                    self.health_msgs,
                    classes=Form.HEALTH_BOX),

                Vertical(
                    Horizontal(
                        self.new_button,
                        self.update_button,
                        self.enable_button,
                        self.disable_button,
                        self.delete_button,
                        classes=BUTTON_ROW_FIELD))),
                
            classes=Form.PANE_BOX)

    def get_p2pool_id(self, instance=None):
        if instance and instance in self.instance_map:
            return self.instance_map[instance]
        return False
    
    def on_mount(self):
        self.radio_set.border_subtitle = DLabel.P2POOL
        form_box = self.query_one("#form_field", Vertical)
        form_box.border_subtitle = DLabel.CONFIG


    def set_data(self, xmrig: XMRig):
        #print(f"XMRig:set_data(): {xmrig}")
        self.xmrig = xmrig
        self.instance_input.value = xmrig.instance()
        self.instance_label.update(xmrig.instance())
        self.num_threads_input.value = str(xmrig.num_threads())
        self.config_label.update(xmrig.config_file())
        
        self.instance_map = xmrig.instance_map()
        instance_list = []
        #print(f"XMRigPane:set_data(): instance_map: {self.instance_map}")
        for instance in self.instance_map.keys():
            instance_list.append(instance)
        self.radio_button_list = instance_list

        # Configure button visibility
        if xmrig.instance():
            # This is an update operation
            self.remove_class(NEW_FIELD)
            self.add_class(UPDATE_FIELD)

            if xmrig.enabled():
                self.remove_class(DISABLE_FIELD)
                self.add_class(ENABLE_FIELD)
            else:
                self.remove_class(ENABLE_FIELD)
                self.add_class(DISABLE_FIELD)
        else:
            # This is a new operation
            self.remove_class(UPDATE_FIELD)
            self.add_class(NEW_FIELD)

        self.health_msgs.update(gen_results_table(xmrig.pop_msgs()))


    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        radio_set = self.query_one("#radio_set", RadioSet)
        if radio_set.pressed_button:
            p2pool_instance = radio_set.pressed_button.label
            if p2pool_instance:
                p2pool = self.instance_map[p2pool_instance]
                self.xmrig.parent(p2pool)
        self.xmrig.instance(self.query_one("#instance_input", Input).value)
        self.xmrig.num_threads(self.query_one("#num_threads_input", Input).value)


        if button_id == NEW_BUTTON_FIELD:
            form_data = {
                TO_MODULE_FIELD: DMod.OPS_MGR,
                TO_METHOD_FIELD: ADD_DEPLOYMENT_FIELD,
                DField.ELEMENT_TYPE: DElem.XMRIG,
                ELEMENT_FIELD: self.xmrig
            }

        elif button_id == UPDATE_BUTTON_FIELD:
            form_data = {
                TO_MODULE_FIELD: DMod.DEPLOYMENT_MGR,
                TO_METHOD_FIELD: DJob.POST_JOB,
                OP_FIELD: DJob.UPDATE,
                DField.ELEMENT_TYPE: DElem.XMRIG,
                ELEMENT_FIELD: self.xmrig,
            }

        elif button_id == ENABLE_BUTTON_FIELD:
            form_data = {
                TO_MODULE_FIELD: DMod.DEPLOYMENT_MGR,
                TO_METHOD_FIELD: DJob.POST_JOB,
                OP_FIELD: DJob.ENABLE,
                DField.ELEMENT_TYPE: DElem.XMRIG,
                ELEMENT_FIELD: self.xmrig,
            }

        elif button_id == DISABLE_BUTTON_FIELD:
            form_data = {
                TO_MODULE_FIELD: DMod.DEPLOYMENT_MGR,
                TO_METHOD_FIELD: DJob.POST_JOB,
                OP_FIELD: DJob.DISABLE,
                DField.ELEMENT_TYPE: DElem.XMRIG,
                ELEMENT_FIELD: self.xmrig,
            }

        elif button_id == DELETE_BUTTON_FIELD:
            form_data = {
                TO_MODULE_FIELD: DMod.DEPLOYMENT_MGR,
                TO_METHOD_FIELD: DJob.POST_JOB,
                OP_FIELD: DJob.DELETE,
                DField.ELEMENT_TYPE: DElem.XMRIG,
                ELEMENT_FIELD: self.xmrig,
            }            

        self.app.post_message(Db4eMsg(self, form_data=form_data))
        #self.app.post_message(RefreshNavPane(self))

    def watch_radio_button_list(self, old, new):
        for child in list(self.radio_set.children):
            child.remove()
        #print(f"XMRigPane:watch_radio_button_list(): instance_map: {self.instance_map}")
        for instance in self.radio_button_list:
            radio_button = RadioButton(instance, classes=RADIO_BUTTON_TYPE_FIELD)
            if self.xmrig.parent() == self.instance_map[instance]:
                radio_button.value = True
            self.radio_set.mount(radio_button)
