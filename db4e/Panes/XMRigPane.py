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
from db4e.Constants.DButton import DButton
from db4e.Constants.DJob import DJob
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DField import DField
from db4e.Constants.DMethod import DMethod
from db4e.Constants.DModule import DModule
from db4e.Constants.DElem import DElem
from db4e.Constants.DForm import DForm


class XMRigPane(Container):

    intro_label = Label("", classes=DForm.INTRO, id=DForm.INTRO)
    instance_label = Label("", id=DForm.INSTANCE_LABEL,classes=DForm.STATIC)
    radio_button_list = reactive([], always_update=True)
    radio_set = RadioSet(id=DForm.RADIO_SET, classes=DForm.RADIO_SET)
    instance_map = {}
    
    config_label = Label("", classes=DForm.STATIC)
    logrotate_config_label = Label("", classes=DForm.STATIC)

    instance_input = Input(
        id=DForm.INSTANCE_INPUT, restrict=f"[a-zA-Z0-9_\-]*", compact=True,
        classes=DForm.INPUT_15)
    num_threads_input = Input(
        id=DForm.NUM_THREADS_INPUT, restrict=f"[0-9]*", compact=True,
        classes=DForm.INPUT_15)
    
    health_msgs = Label()

    analytics_button = Button(label=DLabel.ANALYTICS, id=DButton.ANALYTICS)
    delete_button = Button(label=DLabel.DELETE, id=DButton.DELETE)
    disable_button = Button(label=DLabel.STOP, id=DButton.DISABLE)
    enable_button = Button(label=DLabel.START, id=DButton.ENABLE)
    hashrate_button = Button(label=DLabel.HASHRATE, id=DButton.HASHRATE)
    new_button = Button(label=DLabel.NEW, id=DButton.NEW)
    update_button = Button(label=DLabel.UPDATE, id=DButton.UPDATE)
    view_log_button = Button(label=DLabel.VIEW_LOG, id=DButton.VIEW_LOG)
    xmrig = None


    def compose(self):
        # Remote P2Pool daemon deployment form
        yield Vertical(
            ScrollableContainer(
                self.intro_label,

                Vertical(
                    Horizontal(
                        Label(DLabel.INSTANCE, classes=DForm.FORM_LABEL_25),
                        self.instance_input, self.instance_label),
                    Horizontal(
                        Label(DLabel.NUM_THREADS, classes=DForm.FORM_LABEL_25),
                        self.num_threads_input),
                    Horizontal(
                        Label(DLabel.CONFIG_FILE, classes=DForm.FORM_LABEL_25),
                        self.config_label),
                    Horizontal(
                        Label(DLabel.LOG_ROTATE_CONFIG, classes=DForm.FORM_LABEL_25),
                        self.logrotate_config_label),

                    classes=DForm.FORM_4, id=DForm.FORM_BOX),

                self.radio_set,

                Vertical(
                    self.health_msgs,
                    classes=DForm.HEALTH_BOX, id=DForm.HEALTH_BOX),

                Vertical(
                    Horizontal(
                        self.analytics_button,
                        self.hashrate_button,
                        self.new_button,
                        self.update_button,
                        self.enable_button,
                        self.view_log_button,
                        self.disable_button,
                        self.delete_button,
                        classes=DForm.BUTTON_ROW))),
                
            classes=DForm.PANE_BOX)

    def get_p2pool_id(self, instance=None):
        if instance and instance in self.instance_map:
            return self.instance_map[instance]
        return False
    
    def on_mount(self):
        self.radio_set.border_subtitle = DLabel.P2POOL
        form_box = self.query_one("#" + DForm.FORM_BOX, Vertical)
        form_box.border_subtitle = DLabel.CONFIG
        health_box = self.query_one("#" + DForm.HEALTH_BOX, Vertical)
        health_box.border_subtitle = DLabel.STATUS


    def set_data(self, xmrig: XMRig):
        #print(f"XMRig:set_data(): {xmrig}")
        self.xmrig = xmrig
        self.instance_input.value = xmrig.instance()
        self.instance_label.update(xmrig.instance())
        self.num_threads_input.value = str(xmrig.num_threads())
        self.config_label.update(xmrig.config_file())
        self.logrotate_config_label.update(xmrig.logrotate_config())
        
        self.instance_map = xmrig.instance_map()
        instance_list = []
        print(f"XMRigPane:set_data(): instance_map: {self.instance_map}")
        for instance in self.instance_map.keys():
            instance_list.append(instance)
        self.radio_button_list = instance_list

        # Configure button visibility
        if xmrig.instance():
            # This is an update operation
            INTRO = f"Configure the settings for the " \
            f"[cyan]{xmrig.instance()} {DLabel.XMRIG}[/] deployment. "
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
            INTRO = "Configure the settings for a new " \
            f"[bold cyan]{DLabel.XMRIG}[/] deployment."
            self.remove_class(DField.UPDATE)
            self.add_class(DField.NEW)

        self.intro_label.update(INTRO)
        self.health_msgs.update(gen_results_table(xmrig.pop_msgs()))


    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        radio_set = self.query_one("#" + DForm.RADIO_SET, RadioSet)
        if radio_set.pressed_button:
            p2pool_instance = str(radio_set.pressed_button.label)
            if p2pool_instance:
                p2pool = self.instance_map[p2pool_instance]
                self.xmrig.parent(p2pool)
        self.xmrig.instance(self.query_one("#" + DForm.INSTANCE_INPUT, Input).value)
        self.xmrig.num_threads(self.query_one("#" + DForm.NUM_THREADS_INPUT, Input).value)


        if button_id == DButton.HASHRATE:
            form_data = {
                DField.TO_MODULE: DModule.OPS_MGR,
                DField.TO_METHOD: DMethod.HASHRATES,
                DField.ELEMENT_TYPE: DElem.XMRIG,
                DField.ELEMENT: self.xmrig,
            }

        elif button_id == DButton.NEW:
            form_data = {
                DField.TO_MODULE: DModule.OPS_MGR,
                DField.TO_METHOD: DMethod.ADD_DEPLOYMENT,
                DField.ELEMENT_TYPE: DElem.XMRIG,
                DField.ELEMENT: self.xmrig
            }

        elif button_id == DButton.UPDATE:
            form_data = {
                DField.TO_MODULE: DModule.DEPLOYMENT_CLIENT,
                DField.TO_METHOD: DMethod.UPDATE_DEPLOYMENT,
                DField.ELEMENT_TYPE: DElem.XMRIG,
                DField.ELEMENT: self.xmrig,
            }

        elif button_id == DButton.ENABLE:
            form_data = {
                DField.TO_MODULE: DModule.DEPLOYMENT_CLIENT,
                DField.TO_METHOD: DMethod.ENABLE_DEPLOYMENT,
                DField.ELEMENT_TYPE: DElem.XMRIG,
                DField.ELEMENT: self.xmrig,
            }

        elif button_id == DButton.DISABLE:
            form_data = {
                DField.TO_MODULE: DModule.DEPLOYMENT_CLIENT,
                DField.TO_METHOD: DMethod.DISABLE_DEPLOYMENT,
                DField.ELEMENT_TYPE: DElem.XMRIG,
                DField.ELEMENT: self.xmrig,
            }

        elif button_id == DButton.DELETE:
            form_data = {
                DField.TO_MODULE: DModule.DEPLOYMENT_CLIENT,
                DField.TO_METHOD: DMethod.DELETE_DEPLOYMENT,
                DField.ELEMENT_TYPE: DElem.XMRIG,
                DField.ELEMENT: self.xmrig,
            }
        elif button_id == DButton.VIEW_LOG:
            form_data = {
                DField.ELEMENT_TYPE: DElem.XMRIG,
                DField.TO_MODULE: DModule.OPS_MGR,
                DField.TO_METHOD: DMethod.LOG_VIEWER,
                DField.INSTANCE: self.xmrig.instance()
            }               


        self.app.post_message(Db4eMsg(self, form_data=form_data))
        #self.app.post_message(RefreshNavPane(self))

    def watch_radio_button_list(self, old, new):
        for child in list(self.radio_set.children):
            child.remove()
        #print(f"XMRigPane:watch_radio_button_list(): instance_map: {self.instance_map}")
        for instance in self.radio_button_list:
            radio_button = RadioButton(instance, classes=DForm.RADIO_BUTTON_TYPE)
            if self.xmrig.parent() == self.instance_map[instance]:
                radio_button.value = True
            self.radio_set.mount(radio_button)
