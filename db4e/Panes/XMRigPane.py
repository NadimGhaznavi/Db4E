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
from textual.widgets import Label, Input, Button, RadioSet, RadioButton

from db4e.Modules.Helper import gen_results_table
from db4e.Modules.XMRig import XMRig
from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Constants.DButton import DButton
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DField import DField
from db4e.Constants.DMethod import DMethod
from db4e.Constants.DModule import DModule
from db4e.Constants.DElem import DElem
from db4e.Constants.DForm import DForm


class XMRigPane(Container):

    radio_button_list = reactive([], always_update=True)
    instance_map = {}
    xmrig = None

    def compose(self):
        # Remote P2Pool daemon deployment form
        yield Vertical(
            ScrollableContainer(
                Label("", classes=DForm.INTRO, id=DForm.INTRO),
                Vertical(
                    Horizontal(
                        Label(DLabel.INSTANCE, classes=DForm.FORM_LABEL_25),
                        Input(
                            id=DForm.INSTANCE_INPUT,
                            restrict=f"[a-zA-Z0-9_\-]*",
                            compact=True,
                            classes=DForm.INPUT_15,
                        ),
                        Label("", id=DForm.INSTANCE_LABEL, classes=DForm.STATIC),
                    ),
                    Horizontal(
                        Label(DLabel.NUM_THREADS, classes=DForm.FORM_LABEL_25),
                        Input(
                            id=DForm.NUM_THREADS_INPUT,
                            restrict=f"[0-9]*",
                            compact=True,
                            classes=DForm.INPUT_15,
                        ),
                    ),
                    Horizontal(
                        Label(DLabel.CONFIG_FILE, classes=DForm.FORM_LABEL_25),
                        Label("", id=DForm.CONFIG_LABEL, classes=DForm.STATIC),
                    ),
                    Horizontal(
                        Label(DLabel.LOG_ROTATE_CONFIG, classes=DForm.FORM_LABEL_25),
                        Label(
                            "", id=DForm.LOGROTATE_CONFIG_LABEL, classes=DForm.STATIC
                        ),
                    ),
                    classes=DForm.FORM_4,
                    id=DForm.FORM_BOX,
                ),
                RadioSet(id=DForm.RADIO_SET, classes=DForm.RADIO_SET),
                Vertical(
                    Label(id=DForm.HEALTH_LABEL),
                    classes=DForm.HEALTH_BOX,
                    id=DForm.HEALTH_BOX,
                ),
                Vertical(
                    Horizontal(
                        Button(label=DLabel.HASHRATE, id=DButton.HASHRATE),
                        Button(label=DLabel.SHARES_FOUND, id=DButton.SHARES_FOUND),
                        Button(label=DLabel.NEW, id=DButton.NEW),
                        Button(label=DLabel.UPDATE, id=DButton.UPDATE),
                        Button(label=DLabel.START, id=DButton.ENABLE),
                        Button(label=DLabel.VIEW_LOG, id=DButton.VIEW_LOG),
                        Button(label=DLabel.STOP, id=DButton.DISABLE),
                        Button(label=DLabel.DELETE, id=DButton.DELETE),
                        classes=DForm.BUTTON_ROW,
                    )
                ),
            ),
            classes=DForm.PANE_BOX,
        )

    def get_p2pool_id(self, instance=None):
        if instance and instance in self.instance_map:
            return self.instance_map[instance]
        return False

    def on_mount(self):
        self.query_one(f"#{DForm.RADIO_SET}", RadioSet).border_subtitle = DLabel.P2POOL
        self.query_one(f"#{DForm.FORM_BOX}", Vertical).border_subtitle = DLabel.CONFIG
        self.query_one(f"#{DForm.HEALTH_BOX}", Vertical).border_subtitle = DLabel.STATUS

    def set_data(self, xmrig: XMRig):
        # print(f"XMRig:set_data(): {xmrig}")
        self.xmrig = xmrig
        self.query_one(f"#{DForm.INSTANCE_INPUT}", Input).value = xmrig.instance()
        self.query_one(f"#{DForm.INSTANCE_LABEL}", Label).update(xmrig.instance())
        self.query_one(f"#{DForm.NUM_THREADS_INPUT}", Input).value = str(
            xmrig.num_threads()
        )
        self.query_one(f"#{DForm.CONFIG_LABEL}", Label).update(xmrig.config_file())
        self.query_one(f"#{DForm.LOGROTATE_CONFIG_LABEL}", Label).update(
            xmrig.logrotate_config()
        )

        self.instance_map = xmrig.instance_map()
        instance_list = []
        for instance in self.instance_map.keys():
            instance_list.append(instance)
        self.radio_button_list = instance_list

        # Configure button visibility
        if xmrig.instance():
            # This is an update operation
            INTRO = (
                f"Configure the settings for the "
                f"[cyan]{xmrig.instance()} {DLabel.XMRIG}[/] deployment. "
            )
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
            INTRO = (
                "Configure the settings for a new "
                f"[bold cyan]{DLabel.XMRIG}[/] deployment."
            )
            self.remove_class(DField.UPDATE)
            self.add_class(DField.NEW)

        self.query_one(f"#{DForm.INTRO}", Label).update(INTRO)
        self.query_one(f"#{DForm.HEALTH_LABEL}", Label).update(
            gen_results_table(xmrig.pop_msgs())
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        radio_set = self.query_one(f"#{DForm.RADIO_SET}", RadioSet)
        if radio_set.pressed_button:
            p2pool_instance = str(radio_set.pressed_button.label)
            if p2pool_instance:
                p2pool = self.instance_map[p2pool_instance]
                self.xmrig.parent(p2pool)
        self.xmrig.instance(self.query_one(f"#{DForm.INSTANCE_INPUT}", Input).value)
        self.xmrig.num_threads(
            self.query_one(f"#{DForm.NUM_THREADS_INPUT}", Input).value
        )

        if button_id == DButton.DELETE:
            form_data = {
                DField.TO_MODULE: DModule.DEPLOYMENT_CLIENT,
                DField.TO_METHOD: DMethod.DELETE_DEPLOYMENT,
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

        elif button_id == DButton.ENABLE:
            form_data = {
                DField.TO_MODULE: DModule.DEPLOYMENT_CLIENT,
                DField.TO_METHOD: DMethod.ENABLE_DEPLOYMENT,
                DField.ELEMENT_TYPE: DElem.XMRIG,
                DField.ELEMENT: self.xmrig,
            }

        elif button_id == DButton.HASHRATE:
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
                DField.ELEMENT: self.xmrig,
            }

        elif button_id == DButton.SHARES_FOUND:
            form_data = {
                DField.TO_MODULE: DModule.OPS_MGR,
                DField.TO_METHOD: DMethod.SHARES_FOUND,
                DField.ELEMENT_TYPE: DElem.XMRIG,
                DField.ELEMENT: self.xmrig,
            }

        elif button_id == DButton.UPDATE:
            form_data = {
                DField.TO_MODULE: DModule.DEPLOYMENT_CLIENT,
                DField.TO_METHOD: DMethod.UPDATE_DEPLOYMENT,
                DField.ELEMENT_TYPE: DElem.XMRIG,
                DField.ELEMENT: self.xmrig,
            }

        elif button_id == DButton.VIEW_LOG:
            form_data = {
                DField.ELEMENT_TYPE: DElem.XMRIG,
                DField.TO_MODULE: DModule.OPS_MGR,
                DField.TO_METHOD: DMethod.LOG_VIEWER,
                DField.INSTANCE: self.xmrig.instance(),
            }

        self.app.post_message(Db4eMsg(self, form_data=form_data))
        # self.app.post_message(RefreshNavPane(self))

    def watch_radio_button_list(self, old, new):
        radio_set = self.query_one(f"#{DForm.RADIO_SET}", RadioSet)
        for child in list(radio_set.children):
            child.remove()
        # print(f"XMRigPane:watch_radio_button_list(): instance_map: {self.instance_map}")
        for instance in self.radio_button_list:
            radio_button = RadioButton(instance, classes=DForm.RADIO_BUTTON_TYPE)
            if self.xmrig.parent() == self.instance_map[instance]:
                radio_button.value = True
            radio_set.mount(radio_button)
