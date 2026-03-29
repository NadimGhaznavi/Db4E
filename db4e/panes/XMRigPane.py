# db4e/Panes/XMRigPane.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0


from textual.reactive import reactive
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Label, Input, Button, RadioSet, RadioButton

from db4e.util.Helper import gen_results_table
from db4e.recs.monero.XMRig import XMRig
from db4e.messages.Db4EMsg import Db4EMsg
from db4e.constants.DButton import DButtonF, DButtonL
from db4e.constants.DLabel import DLabel
from db4e.constants.DField import DField
from db4e.constants.DMethod import DMethod
from db4e.constants.DModule import DModule
from db4e.constants.DElem import DElem
from db4e.constants.DForm import DForm


class XMRigPane(Container):
    """Textual pane for XMRigPane."""

    radio_button_list = reactive([], always_update=True)
    instance_map = {}
    xmrig = None

    def compose(self):
        """Compose the pane layout.

        :return: Yielded child widgets for this pane.
        :rtype: ComposeResult
        """
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
                        Button(label=DButtonL.HASHRATE, id=DButtonF.HASHRATE),
                        Button(label=DButtonL.SHARES_FOUND, id=DButtonF.SHARES_FOUND),
                        Button(label=DButtonL.NEW, id=DButtonF.NEW),
                        Button(label=DButtonL.UPDATE, id=DButtonF.UPDATE),
                        Button(label=DButtonL.START, id=DButtonF.ENABLE),
                        Button(label=DButtonL.VIEW_LOG, id=DButtonF.VIEW_LOG),
                        Button(label=DButtonL.STOP, id=DButtonF.DISABLE),
                        Button(label=DButtonL.DELETE, id=DButtonF.DELETE),
                        classes=DForm.BUTTON_ROW,
                    )
                ),
            ),
            classes=DForm.PANE_BOX,
        )

    def get_p2pool_id(self, instance=None):
        """Resolve the selected P2Pool ID.

        :param instance: Instance name.
        :type instance: str
        :return: P2Pool (id, remote_flag) tuple or False.
        :rtype: tuple[int, int] or bool
        """
        if instance and instance in self.instance_map:
            return self.instance_map[instance]
        return False

    def on_mount(self):
        """Handle the mount lifecycle event.

        :return: None
        :rtype: None
        """
        self.query_one(f"#{DForm.RADIO_SET}", RadioSet).border_subtitle = DLabel.P2POOL
        self.query_one(f"#{DForm.FORM_BOX}", Vertical).border_subtitle = DLabel.CONFIG
        self.query_one(f"#{DForm.HEALTH_BOX}", Vertical).border_subtitle = DLabel.STATUS

    def set_data(self, xmrig: XMRig):
        """Set the data for the pane.

        :param xmrig: XMRig deployment object.
        :type xmrig: XMRig
        :return: None
        :rtype: None
        """
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
        print(f"XMRigPane:set_data(): instance_map: {self.instance_map}")
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
                self.remove_class(DField.DISABLED)
                self.add_class(DField.ENABLED)
            else:
                self.remove_class(DField.ENABLED)
                self.add_class(DField.DISABLED)
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
        """Handle button pressed events.

        :param event: Event payload.
        :type event: Button.Pressed
        :return: None
        :rtype: None
        """
        button_id = event.button.id
        radio_set = self.query_one(f"#{DForm.RADIO_SET}", RadioSet)
        if radio_set.pressed_button:
            p2pool_instance = str(radio_set.pressed_button.label)
            if p2pool_instance:
                p2pool_id, remote_flag = self.instance_map[p2pool_instance]
                self.xmrig.parent(p2pool_id)
                self.xmrig.parent_remote(remote_flag)
        self.xmrig.instance(self.query_one(f"#{DForm.INSTANCE_INPUT}", Input).value)
        self.xmrig.num_threads(
            self.query_one(f"#{DForm.NUM_THREADS_INPUT}", Input).value
        )

        # Map button to action
        button_map = {
            DButtonF.DELETE: (DModule.SYNC_CLIENT, DMethod.DELETE_DEPLOYMENT),
            DButtonF.DISABLE: (DModule.DEPLOYMENT_CLIENT, DMethod.DISABLE_DEPLOYMENT),
            DButtonF.ENABLE: (DModule.DEPLOYMENT_CLIENT, DMethod.ENABLE_DEPLOYMENT),
            DButtonF.HASHRATE: (DModule.OPS_MGR, DMethod.HASHRATES),
            DButtonF.NEW: (DModule.SYNC_CLIENT, DMethod.ADD_DEPLOYMENT),
            DButtonF.SHARES_FOUND: (DModule.OPS_MGR, DMethod.SHARES_FOUND),
            DButtonF.UPDATE: (DModule.SYNC_CLIENT, DMethod.UPDATE_DEPLOYMENT),
            DButtonF.VIEW_LOG: (DModule.OPS_MGR, DMethod.LOG_VIEWER),
        }

        if button_id not in button_map:
            raise ValueError(f"No handler for button {button_id}")

        module, method = button_map[button_id]

        form_data = {
            DField.TO_MODULE: module,
            DField.TO_METHOD: method,
            DField.ELEMENT_TYPE: DElem.XMRIG,
            DField.ELEMENT: self.xmrig,
        }

        self.app.post_message(Db4EMsg(self, form_data=form_data))
        # self.app.post_message(RefreshNavPane(self))

    def watch_radio_button_list(self, old, new):
        """React to changes in radio button list.

        :param old: Previous value.
        :type old: list
        :param new: New value.
        :type new: list
        :return: None
        :rtype: None
        """
        radio_set = self.query_one(f"#{DForm.RADIO_SET}", RadioSet)
        for child in list(radio_set.children):
            child.remove()

        ## Get the current XMRig values
        parent_id = None
        remote_flag = None
        if self.xmrig:
            # id value from the p2pool or p2pool_remote table (or -1 if currently disabled)
            parent_id = self.xmrig.parent()
            # if it's 1, then it's the p2pool_remote table, 0 it's the p2pool table, -1 disabled
            remote_flag = self.xmrig.parent_remote()

        for instance in self.radio_button_list:
            radio_button = RadioButton(instance, classes=DForm.RADIO_BUTTON_TYPE)
            cur_parent_id, cur_remote_flag = self.instance_map[instance]
            if parent_id == cur_parent_id and remote_flag == cur_remote_flag:
                radio_button.value = True
            radio_set.mount(radio_button)
