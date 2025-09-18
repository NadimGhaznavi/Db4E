"""
db4e/Panes/P2PoolPane.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from textual.containers import Container, ScrollableContainer, Vertical, Horizontal
from textual.widgets import Label, Input, Button, MarkdownViewer, RadioButton, RadioSet
from textual.reactive import reactive


from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Modules.P2Pool import P2Pool
from db4e.Modules.Helper import gen_results_table
from db4e.Constants.DElem import DElem
from db4e.Constants.DField import DField
from db4e.Constants.DModule import DModule
from db4e.Constants.DMethod import DMethod
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DJob import DJob
from db4e.Constants.DButton import DButton
from db4e.Constants.DForm import DForm


class P2PoolPane(Container):

    instance_label = Label("", id="instance_label",classes=DForm.STATIC)
    radio_button_list = reactive([], always_update=True)
    radio_set = RadioSet(id="radio_set", classes=DForm.RADIO_SET)
    instance_map = {}

    chain_radio_set = RadioSet(id="chain_radio_set", classes=DForm.RADIO_SET)

    config_label = Label("", classes=DForm.STATIC)
    instance_input = Input(
        id="instance_input", restrict=f"[a-zA-Z0-9_\-]*", compact=True,
        classes=DForm.INPUT_30)
    in_peers_input = Input(
        id="in_peers_input", restrict=f"[0-9]*", compact=True,
        classes=DForm.INPUT_30)
    out_peers_input = Input(
        id="out_peers_input", restrict=f"[0-9]*", compact=True,
        classes=DForm.INPUT_30)
    log_level_input = Input(
        id="log_level_input", restrict=f"[0-9]*", compact=True,
        classes=DForm.INPUT_30)
    p2p_port_input = Input(
        id="p2p_port_input", restrict=f"[0-9]*", compact=True,
        classes=DForm.INPUT_30)
    stratum_port_input = Input(
        id="stratum_port_input", restrict=f"[0-9]*", compact=True,
        classes=DForm.INPUT_30)

    health_msgs = Label()

    delete_button = Button(label=DLabel.DELETE, id=DButton.DELETE)
    disable_button = Button(label=DLabel.DISABLE, id=DButton.DISABLE)
    enable_button = Button(label=DLabel.ENABLE, id=DButton.ENABLE)
    new_button = Button(label=DLabel.NEW, id=DButton.NEW)
    update_button = Button(label=DLabel.UPDATE, id=DButton.UPDATE)
    p2pool = None


    def compose(self):

        # Local P2Pool daemon deployment form
        INTRO = "This screen provides a form for creating a new " \
            f"[bold cyan]{DLabel.P2POOL}[/] deployment."

        yield Vertical(
            ScrollableContainer(
                Label(INTRO, classes=DForm.INTRO),

                Vertical(
                    Horizontal(
                        Label(DLabel.INSTANCE, classes=DForm.FORM_LABEL),
                        self.instance_input, self.instance_label),
                    Horizontal(
                        Label(DLabel.IN_PEERS, classes=DForm.FORM_LABEL),
                        self.in_peers_input),
                    Horizontal(
                        Label(DLabel.OUT_PEERS, classes=DForm.FORM_LABEL),
                        self.out_peers_input),
                    Horizontal(
                        Label(DLabel.P2P_PORT, classes=DForm.FORM_LABEL),
                        self.p2p_port_input),
                    Horizontal(
                        Label(DLabel.STRATUM_PORT, classes=DForm.FORM_LABEL),
                        self.stratum_port_input),
                    Horizontal(
                        Label(DLabel.LOG_LEVEL, classes=DForm.FORM_LABEL),
                        self.log_level_input),
                    Horizontal(
                        Label(DLabel.CONFIG_FILE, classes=DForm.FORM_LABEL),
                        self.config_label),
                    classes=DForm.FORM_7, id="form_box"),
                    
                Vertical(
                    self.chain_radio_set),

                Vertical(
                    self.radio_set),

                Vertical(
                    self.health_msgs,
                    classes=DForm.HEALTH_BOX,
                ),

                Vertical(
                    Horizontal(
                        self.new_button,
                        self.update_button,
                        self.enable_button,
                        self.disable_button,
                        self.delete_button,
                        classes=DForm.BUTTON_ROW))),
                
            classes=DForm.PANE_BOX)


    def on_mount(self):
        #radio_set = self.query_one("#radio_set", RadioSet")
        self.radio_set.border_subtitle = DLabel.UPSTREAM_MONERO
        self.chain_radio_set.border_subtitle = DLabel.CHAIN
        form_box = self.query_one("#form_box", Vertical)
        form_box.border_subtitle = DLabel.CONFIG        

    def set_data(self, p2pool: P2Pool):
        self.p2pool = p2pool
        self.instance_input.value = p2pool.instance()
        self.instance_label.update(p2pool.instance())
        self.config_label.update(p2pool.config_file())
        self.in_peers_input.value = str(p2pool.in_peers())
        self.out_peers_input.value = str(p2pool.out_peers())
        self.p2p_port_input.value = str(p2pool.p2p_port())
        self.stratum_port_input.value = str(p2pool.stratum_port())
        self.log_level_input.value = str(p2pool.log_level())

        # Create the Monerod radio buttons
        self.instance_map = p2pool.instance_map()
        print(f"P2PoolPane:set_data(): instance_map: {self.instance_map}")
        instance_list = []
        for instance in p2pool.instance_map().keys():
            instance_list.append(instance)
        self.radio_button_list = instance_list

        # Create the chain radio buttons
        for child in list(self.chain_radio_set.children):
            child.remove()
        for chain in ['mainchain', 'minisidechain', 'nanosidechain']:
            radio_button = RadioButton(chain, classes=DForm.RADIO_BUTTON_TYPE)
            if p2pool.chain() == chain:
                radio_button.value = True
            self.chain_radio_set.mount(radio_button)

        # Configure button visibility
        if p2pool.instance():
            # This is an update operation
            self.remove_class(DField.NEW)
            self.add_class(DField.UPDATE)

            if p2pool.enabled():
                self.remove_class(DField.DISABLE)
                self.add_class(DField.ENABLE)
            else:
                self.remove_class(DField.ENABLE)
                self.add_class(DField.DISABLE)
        else:
            # This is a new operation
            self.remove_class(DField.UPDATE)
            self.add_class(DField.NEW)

        self.health_msgs.update(gen_results_table(p2pool.pop_msgs()))                    


    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        radio_set = self.query_one("#radio_set", RadioSet)
        monerod_instance = None
        monerod_id = None
        if radio_set.pressed_button:
            monerod_instance = str(radio_set.pressed_button.label)
            monerod_id = self.instance_map[monerod_instance]
        
        chain_radio_set = self.query_one("#chain_radio_set", RadioSet)
        chain = None
        if chain_radio_set.pressed_button:
            chain = chain_radio_set.pressed_button.label
            
        self.p2pool.parent(monerod_id)
        self.p2pool.chain(str(chain))
        self.p2pool.instance(self.query_one("#instance_input", Input).value)
        self.p2pool.in_peers(self.query_one("#in_peers_input", Input).value)
        self.p2pool.out_peers(self.query_one("#out_peers_input", Input).value)
        self.p2pool.p2p_port(self.query_one("#p2p_port_input", Input).value)
        self.p2pool.stratum_port(self.query_one("#stratum_port_input", Input).value)
        self.p2pool.log_level(self.query_one("#log_level_input", Input).value)

        if button_id == DButton.NEW:
            form_data = {
                DField.TO_MODULE: DModule.OPS_MGR,
                DField.TO_METHOD: DMethod.ADD_DEPLOYMENT,
                DField.ELEMENT_TYPE: DElem.P2POOL,
                DField.ELEMENT: self.p2pool,
            }

        elif button_id == DButton.UPDATE:
            form_data = {
                DField.TO_MODULE: DModule.DEPLOYMENT_CLIENT,
                DField.TO_METHOD: DMethod.UPDATE_DEPLOYMENT,
                DField.ELEMENT_TYPE: DElem.P2POOL,
                DField.ELEMENT: self.p2pool,
            }

        elif button_id == DButton.ENABLE:
            form_data = {
                DField.TO_MODULE: DModule.DEPLOYMENT_CLIENT,
                DField.TO_METHOD: DMethod.ENABLE_DEPLOYMENT,
                DField.ELEMENT_TYPE: DElem.P2POOL,
                DField.ELEMENT: self.p2pool,
            }

        elif button_id == DButton.DISABLE:
            form_data = {
                DField.TO_MODULE: DModule.DEPLOYMENT_CLIENT,
                DField.TO_METHOD: DMethod.DISABLE_DEPLOYMENT,
                DField.ELEMENT_TYPE: DElem.P2POOL,
                DField.ELEMENT: self.p2pool,
            }

        elif button_id == DButton.DELETE:
            form_data = {
                DField.TO_MODULE: DModule.DEPLOYMENT_CLIENT,
                DField.TO_METHOD: DMethod.DELETE_DEPLOYMENT,
                DField.ELEMENT_TYPE: DElem.P2POOL,
                DField.ELEMENT: self.p2pool,
            }            

        self.app.post_message(Db4eMsg(self, form_data=form_data))

    
    def watch_radio_button_list(self, old, new):
        for child in list(self.radio_set.children):
            child.remove()
        for instance in self.radio_button_list:
            radio_button = RadioButton(instance, classes=DForm.RADIO_BUTTON_TYPE)
            if self.p2pool.parent() == self.instance_map[instance]:
                radio_button.value = True
            self.radio_set.mount(radio_button)