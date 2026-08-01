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
from db4e.constants.DLabel import DLabel as LABEL
from db4e.constants.DField import DField as FIELD
from db4e.constants.DMethod import DMethod as METHOD
from db4e.constants.DModule import DModule as MODULE
from db4e.constants.DElem import DElem as ELEM
from db4e.constants.DForm import DForm as FORM
from db4e.constants.DStatus import DStatus as STATUS


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
                Label("", classes=FORM.INTRO, id=FORM.INTRO),
                Vertical(
                    Horizontal(
                        Label(LABEL.INSTANCE, classes=FORM.FORM_LABEL_25),
                        Input(
                            id=FORM.INSTANCE_INPUT,
                            restrict=f"[a-zA-Z0-9_\-]*",
                            compact=True,
                            classes=FORM.INPUT_15,
                        ),
                        Label("", id=FORM.INSTANCE_LABEL, classes=FORM.STATIC),
                    ),
                    Horizontal(
                        Label(LABEL.NUM_THREADS, classes=FORM.FORM_LABEL_25),
                        Input(
                            id=FORM.NUM_THREADS_INPUT,
                            restrict=f"[0-9]*",
                            compact=True,
                            classes=FORM.INPUT_15,
                        ),
                    ),
                    Horizontal(
                        Label(LABEL.HTTP_PORT, classes=FORM.FORM_LABEL_25),
                        Input(
                            id=FORM.HTTP_PORT,
                            restrict=f"[0-9]*",
                            compact=True,
                            classes=FORM.INPUT_15,
                        ),
                    ),
                    Horizontal(
                        Label(LABEL.CONFIG_FILE, classes=FORM.FORM_LABEL_25),
                        Label("", id=FORM.CONFIG_LABEL, classes=FORM.STATIC),
                    ),
                    Horizontal(
                        Label(LABEL.LOG_ROTATE_CONFIG, classes=FORM.FORM_LABEL_25),
                        Label(
                            "", id=FORM.LOGROTATE_CONFIG_LABEL, classes=FORM.STATIC
                        ),
                    ),
                    classes=FORM.FORM_5,
                    id=FORM.FORM_BOX,
                ),
                RadioSet(id=FORM.RADIO_SET, classes=FORM.RADIO_SET),
                Vertical(
                    Label(id=FORM.HEALTH_LABEL),
                    classes=FORM.HEALTH_BOX,
                    id=FORM.HEALTH_BOX,
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
                        classes=FORM.BUTTON_ROW,
                    )
                ),
            ),
            classes=FORM.PANE_BOX,
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
        self.query_one(f"#{FORM.RADIO_SET}", RadioSet).border_subtitle = LABEL.P2POOL
        self.query_one(f"#{FORM.FORM_BOX}", Vertical).border_subtitle = LABEL.CONFIG
        self.query_one(f"#{FORM.HEALTH_BOX}", Vertical).border_subtitle = LABEL.STATUS

    def set_data(self, xmrig: XMRig):
        """Set the data for the pane.

        :param xmrig: XMRig deployment object.
        :type xmrig: XMRig
        :return: None
        :rtype: None
        """
        # If the upstream p2pool is undefined, then the start/stop/restart
        # buttons are hidden
        if xmrig.parent() == FIELD.DISABLE:
            self.add_class(STATUS.NO_UPSTREAM)
            self.remove_class(STATUS.IS_RUNNING)

        # Hide the start/stop button
        elif xmrig.is_running():
            self.remove_class(STATUS.IS_STOPPED)
            self.add_class(STATUS.IS_RUNNING)

        # Hid the stop/restart button
        else:
            self.remove_class(STATUS.IS_RUNNING)
            self.add_class(STATUS.IS_STOPPED)

        self.xmrig = xmrig

        if xmrig.instance():
            self.add_class(FIELD.EDIT)
            # This is an update operation
            INTRO = (
                f"Configure the settings for the "
                f"[cyan]{xmrig.instance()} {LABEL.XMRIG}[/] deployment. "
            )
        else:
            # This is a new operation
            self.remove_class(FIELD.UPDATE)
            self.add_class(FIELD.NEW)
            INTRO = (
                "Configure the settings for a new "
                f"[bold cyan]{LABEL.XMRIG}[/] deployment."
            )

        self.query_one(f"#{FORM.HTTP_PORT}", Input).value = str(xmrig.http_port())
        self.query_one(f"#{FORM.INSTANCE_INPUT}", Input).value = xmrig.instance()
        self.query_one(f"#{FORM.INSTANCE_LABEL}", Label).update(xmrig.instance())
        self.query_one(f"#{FORM.NUM_THREADS_INPUT}", Input).value = str(
            xmrig.num_threads()
        )
        self.query_one(f"#{FORM.CONFIG_LABEL}", Label).update(xmrig.config_file())
        self.query_one(f"#{FORM.LOGROTATE_CONFIG_LABEL}", Label).update(
            xmrig.logrotate_config()
        )

        self.instance_map = xmrig.instance_map()
        self.radio_button_list = list(self.instance_map.keys())

        self.query_one(f"#{FORM.INTRO}", Label).update(INTRO)
        self.query_one(f"#{FORM.HEALTH_LABEL}", Label).update(
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
        radio_set = self.query_one(f"#{FORM.RADIO_SET}", RadioSet)
        if radio_set.pressed_button:
            p2pool_instance = str(radio_set.pressed_button.label)
            if p2pool_instance:
                p2pool_id, remote_flag = self.instance_map[p2pool_instance]
                self.xmrig.parent(p2pool_id)
                self.xmrig.parent_remote(remote_flag)
        self.xmrig.instance(self.query_one(f"#{FORM.INSTANCE_INPUT}", Input).value)
        self.xmrig.num_threads(
            self.query_one(f"#{FORM.NUM_THREADS_INPUT}", Input).value
        )
        self.xmrig.http_port(
            self.query_one(f"#{FORM.HTTP_PORT}", Input).value
        )

        # Map button to action
        button_map = {
            DButtonF.DELETE: (MODULE.SYNC_CLIENT, METHOD.DELETE_DEPLOYMENT),
            DButtonF.DISABLE: (MODULE.SYNC_CLIENT, METHOD.STOP),
            DButtonF.ENABLE: (MODULE.SYNC_CLIENT, METHOD.START),
            DButtonF.HASHRATE: (MODULE.OPS_MGR, METHOD.HASHRATES),
            DButtonF.NEW: (MODULE.SYNC_CLIENT, METHOD.ADD_DEPLOYMENT),
            DButtonF.SHARES_FOUND: (MODULE.OPS_MGR, METHOD.SHARES_FOUND),
            DButtonF.UPDATE: (MODULE.SYNC_CLIENT, METHOD.UPDATE_DEPLOYMENT),
            DButtonF.VIEW_LOG: (MODULE.OPS_MGR, METHOD.LOG_VIEWER),
        }

        if button_id not in button_map:
            raise ValueError(f"No handler for button {button_id}")

        module, method = button_map[button_id]

        form_data = {
            FIELD.TO_MODULE: module,
            FIELD.TO_METHOD: method,
            FIELD.ELEMENT_TYPE: ELEM.XMRIG,
            FIELD.ELEMENT: self.xmrig,
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
        radio_set = self.query_one(f"#{FORM.RADIO_SET}", RadioSet)
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
            radio_button = RadioButton(instance, classes=FORM.RADIO_BUTTON_TYPE)
            cur_parent_id, cur_remote_flag = self.instance_map[instance]
            if parent_id == cur_parent_id and remote_flag == cur_remote_flag:
                radio_button.value = True
            radio_set.mount(radio_button)
