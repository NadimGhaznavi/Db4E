# db4e/Panes/P2PoolInternalPane.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
#    GitHub: https://github.com/NadimGhaznavi/db4e
#    License: GPL 3.0


from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Label, Button

from db4e.util.Helper import gen_results_table
from db4e.recs.monero.P2PoolInternal import P2PoolInternal

from db4e.messages.Db4EMsg import Db4EMsg

from db4e.constants.DButton import DButtonF, DButtonL
from db4e.constants.DLabel import DLabel
from db4e.constants.DField import DField
from db4e.constants.DMethod import DMethod
from db4e.constants.DModule import DModule
from db4e.constants.DElem import DElem
from db4e.constants.DForm import DForm
from db4e.constants.DStatus import DStatus


class ChainPane(Container):
    """Textual pane for ChainPane."""

    p2pool = None

    def compose(self):
        """Compose the pane layout.

        :return: Yielded child widgets for this pane.
        :rtype: ComposeResult
        """
        # Internal P2Pool daemon analythics form
        INTRO = f"View information about the [cyan]{DLabel.P2POOL_INTERNAL}[/] deployment here."

        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=DForm.INTRO, id=DForm.INTRO),
                Vertical(
                    Horizontal(
                        Label(DLabel.INSTANCE, classes=DForm.FORM_LABEL),
                        Label("", id=DForm.INSTANCE_LABEL, classes=DForm.STATIC),
                    ),
                    Horizontal(
                        Label(DLabel.IN_PEERS, classes=DForm.FORM_LABEL),
                        Label("", id=DForm.IN_PEERS_LABEL, classes=DForm.STATIC),
                    ),
                    Horizontal(
                        Label(DLabel.OUT_PEERS, classes=DForm.FORM_LABEL),
                        Label("", id=DForm.OUT_PEERS_LABEL, classes=DForm.STATIC),
                    ),
                    Horizontal(
                        Label(DLabel.P2P_PORT, classes=DForm.FORM_LABEL),
                        Label("", id=DForm.P2P_PORT_LABEL, classes=DForm.STATIC),
                    ),
                    Horizontal(
                        Label(DLabel.STRATUM_PORT, classes=DForm.FORM_LABEL),
                        Label("", id=DForm.STRATUM_PORT_LABEL, classes=DForm.STATIC),
                    ),
                    Horizontal(
                        Label(DLabel.LOG_LEVEL, classes=DForm.FORM_LABEL),
                        Label("", id=DForm.LOG_LEVEL_LABEL, classes=DForm.STATIC),
                    ),
                    Horizontal(
                        Label(DLabel.CONFIG_FILE, classes=DForm.FORM_LABEL),
                        Label("", id=DForm.CONFIG_FILE_LABEL, classes=DForm.STATIC),
                    ),
                    id=DForm.FORM_BOX,
                    classes=DForm.FORM_7,
                ),
                Vertical(
                    Label(id=DForm.HEALTH_LABEL),
                    classes=DForm.HEALTH_BOX,
                    id=DForm.HEALTH_BOX,
                ),
                Vertical(
                    Horizontal(
                        Button(label=DButtonL.BLOCKS_FOUND, id=DButtonF.BLOCKS_FOUND),
                        Button(label=DButtonL.HASHRATE, id=DButtonF.HASHRATE),
                        Button(label=DButtonL.VIEW_LOG, id=DButtonF.VIEW_LOG),
                        Button(label=DButtonL.RESTART, id=DButtonF.RESTART),
                        Button(label=DButtonL.START, id=DButtonF.START),
                        Button(label=DButtonL.STOP, id=DButtonF.STOP),
                        classes=DForm.BUTTON_ROW,
                    )
                ),
            ),
            classes=DForm.PANE_BOX,
        )

    def on_mount(self):
        """Handle the mount lifecycle event.

        :return: None
        :rtype: None
        """
        self.query_one("#" + DForm.FORM_BOX, Vertical).border_subtitle = DLabel.CONFIG
        self.query_one("#" + DForm.HEALTH_BOX, Vertical).border_subtitle = DLabel.STATUS

    def set_data(self, p2pool: P2PoolInternal):
        """Set the data for the pane.

        :param p2pool: P2Pool deployment object.
        :type p2pool: P2PoolInternal
        :return: None
        :rtype: None
        """

        # If the upstream monero is undefined, then the start/stop/restart
        # buttons are hidden
        if p2pool.parent() == DField.DISABLE:
            self.add_class(DStatus.NO_UPSTREAM)
            self.remove_class(DStatus.IS_STOPPED)
            self.remove_class(DStatus.IS_RUNNING)

        # Hide the start button
        elif p2pool.is_running():
            self.remove_class(DStatus.IS_STOPPED)
            self.add_class(DStatus.IS_RUNNING)

        # Hide the stop/restart button
        else:
            self.remove_class(DStatus.IS_RUNNING)
            self.add_class(DStatus.IS_STOPPED)

        self.p2pool = p2pool
        self.query_one(f"#{DForm.INSTANCE_LABEL}", Label).update(p2pool.instance())
        self.query_one(f"#{DForm.CONFIG_FILE_LABEL}", Label).update(
            p2pool.config_file()
        )
        self.query_one(f"#{DForm.IN_PEERS_LABEL}", Label).update(str(p2pool.in_peers()))
        self.query_one(f"#{DForm.OUT_PEERS_LABEL}", Label).update(
            str(p2pool.out_peers())
        )
        self.query_one(f"#{DForm.P2P_PORT_LABEL}", Label).update(str(p2pool.p2p_port()))
        self.query_one(f"#{DForm.STRATUM_PORT_LABEL}", Label).update(
            str(p2pool.stratum_port())
        )
        self.query_one(f"#{DForm.LOG_LEVEL_LABEL}", Label).update(
            str(p2pool.log_level())
        )
        # Health messages
        self.query_one(f"#{DForm.HEALTH_LABEL}", Label).update(
            gen_results_table(p2pool.pop_msgs())
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button pressed events.

        :param event: Event payload.
        :type event: Button.Pressed
        :return: None
        :rtype: None
        """
        button_id = event.button.id

        if button_id == DButtonF.BLOCKS_FOUND:
            form_data = {
                DField.TO_MODULE: DModule.OPS_MGR,
                DField.TO_METHOD: DMethod.BLOCKS_FOUND,
                DField.ELEMENT_TYPE: DElem.P2POOL_INTERNAL,
                DField.ELEMENT: self.p2pool,
            }

        if button_id == DButtonF.HASHRATE:
            form_data = {
                DField.TO_MODULE: DModule.OPS_MGR,
                DField.TO_METHOD: DMethod.HASHRATES,
                DField.ELEMENT_TYPE: DElem.P2POOL_INTERNAL,
                DField.ELEMENT: self.p2pool,
            }

        elif button_id == DButtonF.RESTART:
            form_data = {
                DField.ELEMENT_TYPE: DElem.P2POOL_INTERNAL,
                DField.TO_MODULE: DModule.DEPLOYMENT_CLIENT,
                DField.TO_METHOD: DMethod.RESTART,
                DField.INSTANCE: self.p2pool.instance(),
            }

        elif button_id == DButtonF.START:
            form_data = {
                DField.ELEMENT_TYPE: DElem.P2POOL_INTERNAL,
                DField.TO_MODULE: DModule.SYNC_CLIENT,
                DField.TO_METHOD: DMethod.START,
                DField.ELEMENT: self.p2pool,
            }

        elif button_id == DButtonF.STOP:
            form_data = {
                DField.ELEMENT_TYPE: DElem.P2POOL_INTERNAL,
                DField.TO_MODULE: DModule.DEPLOYMENT_CLIENT,
                DField.TO_METHOD: DMethod.STOP,
                DField.INSTANCE: self.p2pool.instance(),
            }

        elif button_id == DButtonF.VIEW_LOG:
            form_data = {
                DField.ELEMENT_TYPE: DElem.P2POOL_INTERNAL,
                DField.TO_MODULE: DModule.OPS_MGR,
                DField.TO_METHOD: DMethod.LOG_VIEWER,
                DField.INSTANCE: self.p2pool.instance(),
            }

        self.app.post_message(Db4EMsg(self, form_data=form_data))
