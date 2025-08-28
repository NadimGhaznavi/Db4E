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
    BUTTON_ROW_FIELD, DELETE_BUTTON_FIELD, DELETE_LABEL, ENABLE_BUTTON_FIELD, 
    ENABLE_LABEL, DISABLE_BUTTON_FIELD, DISABLE_LABEL,
    UPDATE_BUTTON_FIELD, NEW_BUTTON_FIELD, NEW_LABEL, UPDATE_LABEL)
from db4e.Constants.Fields import (
    ADD_DEPLOYMENT_FIELD, NEW_FIELD,
    FORM_3_FIELD, FORM_INPUT_15_FIELD, DISABLE_FIELD, FORM_INTRO_FIELD,
    FORM_LABEL_FIELD, HEALTH_BOX_FIELD, ELEMENT_FIELD,
    INSTANCE_FIELD, ENABLE_FIELD, OPS_MGR_FIELD,
    PANE_BOX_FIELD, 
    RADIO_BUTTON_TYPE_FIELD, RADIO_SET_FIELD, 
    STATIC_CONTENT_FIELD, TO_METHOD_FIELD, TO_MODULE_FIELD,
    UPDATE_DEPLOYMENT_FIELD, XMRIG_FIELD, ELEMENT_TYPE_FIELD)
from db4e.Constants.Jobs import(
    JOB_QUEUE_FIELD, OP_FIELD, POST_JOB_FIELD, DELETE_FIELD, UPDATE_FIELD
)
from db4e.Constants.Labels import (
    CONFIG_LABEL, INSTANCE_LABEL,
    NUM_THREADS_LABEL, XMRIG_LABEL)


class XMRigPane(Container):

    radio_button_list = reactive([], always_update=True)
    radio_set = RadioSet(id="radio_set", classes=RADIO_SET_FIELD)
    instance_map = {}
    
    config_label = Label("", classes=STATIC_CONTENT_FIELD)
    instance_input = Input(
        id="instance_input", restrict=f"[a-zA-Z0-9_\-]*", compact=True,
        classes=FORM_INPUT_15_FIELD)
    num_threads_input = Input(
        id="num_threads_input", restrict=f"[0-9]*", compact=True,
        classes=FORM_INPUT_15_FIELD)
    
    health_msgs = Label()

    delete_button = Button(label=DELETE_LABEL, id=DELETE_BUTTON_FIELD)
    disable_button = Button(label=DISABLE_LABEL, id=DISABLE_BUTTON_FIELD)
    enable_button = Button(label=ENABLE_LABEL, id=ENABLE_BUTTON_FIELD)
    new_button = Button(label=NEW_LABEL, id=NEW_BUTTON_FIELD)
    update_button = Button(label=UPDATE_LABEL, id=UPDATE_BUTTON_FIELD)
    xmrig = None


    def compose(self):
        # Remote P2Pool daemon deployment form
        INTRO = f"View and edit the deployment settings for the " \
            f"[cyan]{XMRIG_LABEL}[/] deployment here."


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
                    Horizontal(
                        Label(NUM_THREADS_LABEL, classes=FORM_LABEL_FIELD),
                        self.num_threads_input),
                    classes=FORM_3_FIELD),

                Vertical(
                    self.radio_set),

                Vertical(
                    self.health_msgs,
                    classes=HEALTH_BOX_FIELD),

                Vertical(
                    Horizontal(
                        self.new_button,
                        self.update_button,
                        self.enable_button,
                        self.disable_button,
                        self.delete_button,
                        classes=BUTTON_ROW_FIELD))),
                
            classes=PANE_BOX_FIELD)

    def get_p2pool_id(self, instance=None):
        if instance and instance in self.instance_map:
            return self.instance_map[instance]
        return False

    def set_data(self, xmrig: XMRig):
        #print(f"XMRig:set_data(): {xmrig}")
        self.xmrig = xmrig
        self.instance_input.value = xmrig.instance()
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
        p2pool_instance = radio_set.pressed_button.label
        if p2pool_instance:
            p2pool = self.instance_map[p2pool_instance]
            self.xmrig.parent(p2pool)
        self.xmrig.instance(self.query_one("#instance_input", Input).value)
        self.xmrig.num_threads(self.query_one("#num_threads_input", Input).value)


        if button_id == NEW_BUTTON_FIELD:
            form_data = {
                ELEMENT_TYPE_FIELD: XMRIG_FIELD,
                TO_MODULE_FIELD: OPS_MGR_FIELD,
                TO_METHOD_FIELD: ADD_DEPLOYMENT_FIELD,
                ELEMENT_FIELD: self.xmrig
            }

        elif button_id == UPDATE_BUTTON_FIELD:
            form_data = {
                ELEMENT_TYPE_FIELD: XMRIG_FIELD,
                TO_MODULE_FIELD: JOB_QUEUE_FIELD,
                TO_METHOD_FIELD: POST_JOB_FIELD,
                OP_FIELD: UPDATE_FIELD,
                ELEMENT_FIELD: self.xmrig,
                INSTANCE_FIELD: self.xmrig.instance()
            }

        elif button_id == ENABLE_BUTTON_FIELD:
            form_data = {
                ELEMENT_TYPE_FIELD: XMRIG_FIELD,
                TO_MODULE_FIELD: JOB_QUEUE_FIELD,
                TO_METHOD_FIELD: POST_JOB_FIELD,
                OP_FIELD: ENABLE_FIELD,
                ELEMENT_FIELD: self.xmrig,
                INSTANCE_FIELD: self.xmrig.instance()
            }

        elif button_id == DISABLE_BUTTON_FIELD:
            form_data = {
                ELEMENT_TYPE_FIELD: XMRIG_FIELD,
                TO_MODULE_FIELD: JOB_QUEUE_FIELD,
                TO_METHOD_FIELD: POST_JOB_FIELD,
                OP_FIELD: DISABLE_FIELD,
                ELEMENT_FIELD: self.xmrig,
                INSTANCE_FIELD: self.xmrig.instance()
            }

        elif button_id == DELETE_BUTTON_FIELD:
            form_data = {
                ELEMENT_TYPE_FIELD: XMRIG_FIELD,
                TO_MODULE_FIELD: JOB_QUEUE_FIELD,
                TO_METHOD_FIELD: POST_JOB_FIELD,
                OP_FIELD: DELETE_FIELD,
                ELEMENT_FIELD: self.xmrig,
                INSTANCE_FIELD: self.xmrig.instance()
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
