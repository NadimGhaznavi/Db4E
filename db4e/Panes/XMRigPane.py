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
from db4e.Constants.Buttons import DButton
from db4e.Constants.Jobs import DJob
from db4e.Constants.Labels import DLabel
from db4e.Constants.Form import Form
from db4e.Constants.Fields import DField, DMod, DElem, Method




class XMRigPane(Container):

    instance_label = Label("", id="instance_label",classes=Form.STATIC.value)
    radio_button_list = reactive([], always_update=True)
    radio_set = RadioSet(id="radio_set", classes=Form.RADIO_SET.value)
    instance_map = {}
    
    config_label = Label("", classes=Form.STATIC.value)
    instance_input = Input(
        id="instance_input", restrict=f"[a-zA-Z0-9_\-]*", compact=True,
        classes=Form.INPUT_15.value)
    num_threads_input = Input(
        id="num_threads_input", restrict=f"[0-9]*", compact=True,
        classes=Form.INPUT_15.value)
    
    health_msgs = Label()

    delete_button = Button(label=DLabel.DELETE.value, id=DButton.DELETE.value)
    disable_button = Button(label=DLabel.DISABLE.value, id=DButton.DISABLE.value)
    enable_button = Button(label=DLabel.ENABLE.value, id=DButton.ENABLE.value)
    new_button = Button(label=DLabel.NEW.value, id=DButton.NEW.value)
    update_button = Button(label=DLabel.UPDATE.value, id=DButton.UPDATE.value)
    xmrig = None


    def compose(self):
        # Remote P2Pool daemon deployment form
        INTRO = f"View and edit the deployment settings for the " \
            f"[cyan]{DLabel.XMRIG}[/] deployment here."


        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=Form.INTRO.value),

                Vertical(
                    Horizontal(
                        Label(DLabel.INSTANCE.value, classes=Form.FORM_LABEL.value),
                        self.instance_input, self.instance_label),
                    Horizontal(
                        Label(DLabel.NUM_THREADS.value, classes=Form.FORM_LABEL.value),
                        self.num_threads_input),
                    Horizontal(
                        Label(DLabel.CONFIG_FILE.value, classes=Form.FORM_LABEL.value),
                        self.config_label),
                    classes=Form.FORM_3.value, id="form_field"),

                Vertical(
                    self.radio_set),

                Vertical(
                    self.health_msgs,
                    classes=Form.HEALTH_BOX.value),

                Vertical(
                    Horizontal(
                        self.new_button,
                        self.update_button,
                        self.enable_button,
                        self.disable_button,
                        self.delete_button,
                        classes=Form.BUTTON_ROW.value))),
                
            classes=Form.PANE_BOX.value)

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
            self.remove_class(DField.NEW)
            self.add_class(DField.UPDATE)

            if xmrig.enabled():
                self.remove_class(DField.DISABLE)
                self.add_class(DField.ENABLE)
            else:
                self.remove_class(DField.ENABLE)
                self.add_class(DField.DISABLE)
        else:
            # This is a new operation
            self.remove_class(DField.UPDATE)
            self.add_class(DField.NEW)

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


        if button_id == DButton.NEW:
            form_data = {
                DField.TO_MODULE: DMod.OPS_MGR,
                DField.TO_METHOD: Method.ADD_DEPLOYMENT,
                DField.ELEMENT_TYPE: DElem.XMRIG,
                DField.ELEMENT: self.xmrig
            }

        elif button_id == DButton.UPDATE:
            form_data = {
                DField.TO_MODULE: DMod.DEPLOYMENT_MGR,
                DField.TO_METHOD: Method.POST_JOB,
                DField.OP: DJob.UPDATE,
                DField.ELEMENT_TYPE: DElem.XMRIG,
                DField.ELEMENT: self.xmrig,
            }

        elif button_id == DButton.ENABLE:
            form_data = {
                DField.TO_MODULE: DMod.DEPLOYMENT_MGR,
                DField.TO_METHOD: Method.POST_JOB,
                DField.OP: DJob.ENABLE,
                DField.ELEMENT_TYPE: DElem.XMRIG,
                DField.ELEMENT: self.xmrig,
            }

        elif button_id == DButton.DISABLE:
            form_data = {
                DField.TO_MODULE: DMod.DEPLOYMENT_MGR,
                DField.TO_METHOD: Method.POST_JOB,
                DField.OP: DJob.DISABLE,
                DField.ELEMENT_TYPE: DElem.XMRIG,
                DField.ELEMENT: self.xmrig,
            }

        elif button_id == DButton.DELETE:
            form_data = {
                DField.TO_MODULE: DMod.DEPLOYMENT_MGR,
                DField.TO_METHOD: Method.POST_JOB,
                DField.OP: DJob.DELETE,
                DField.ELEMENT_TYPE: DElem.XMRIG,
                DField.ELEMENT: self.xmrig,
            }            

        self.app.post_message(Db4eMsg(self, form_data=form_data))
        #self.app.post_message(RefreshNavPane(self))

    def watch_radio_button_list(self, old, new):
        for child in list(self.radio_set.children):
            child.remove()
        #print(f"XMRigPane:watch_radio_button_list(): instance_map: {self.instance_map}")
        for instance in self.radio_button_list:
            radio_button = RadioButton(instance, classes=Form.RADIO_BUTTON_TYPE)
            if self.xmrig.parent() == self.instance_map[instance]:
                radio_button.value = True
            self.radio_set.mount(radio_button)
