#!/opt/prod/db4e/venv/bin/python

import urwid

DB4E_CORE = ['db4e', 'p2pool', 'xmrig', 'monerod', 'repo']

DISPLAY_NAMES = {
    'db4e': 'db4e core',
    'p2pool': 'P2Pool daemon',
    'xmrig': 'XMRig miner',
    'monerod': 'Monero daemon',
    'repo': 'Website repo'
}

PALETTE = [
    ('na', '', ''),
    ('title', 'dark green, bold', ''),
    
    ('bold', 'bold', ''),
    ('running', 'dark green,bold', ''),
    ('stopped', 'dark red', ''),
    ('not_installed', 'yellow', ''),
    ('button', 'light cyan,bold', ''),
    ('reversed', 'standout', '')
]


# Dummy model for status reporting and probing
class Db4eModel:
    def __init__(self):
        # ['db4e', 'p2pool', 'xmrig', 'monerod', 'repo']
        self.daemons = DB4E_CORE
        
    def get_daemons(self):
        return self.daemons

    def get_daemon_status(self, name):
        # TODO: Replace with actual probe logic
        if name == 'db4e':
            return ('✅', 'running')
        elif name == 'p2pool':
            return ('❌', 'stopped')
        elif name == 'mongodb':
            return ('✅', 'running')
        elif name == 'xmrig':
            return ('⚠️', 'not_installed')
        elif name == 'monerod':
            return ('✅', 'running')
        elif name == 'repo':
            return ('✅', 'running')
        else:
            return ('N/A', 'not_installed')

    def set_main_screen(self, data):
        self._main_screen = data

class Db4eTui:
    def __init__(self):
        self.model = Db4eModel()

        self.daemon_radios = []
        self.right_panel = urwid.Text(('bold', "COMPONENT INFO"))
        self.right_panel = urwid.LineBox(
            urwid.Text(('bold', "COMPONENT INFO")),
            title='TIME', title_align="right", title_attr="title"
        )
        
        self.main_loop = urwid.MainLoop(self.build_main_frame(), PALETTE, unhandled_input=self.exit_on_q)

    def build_daemon_list(self):
        body = []
        group = []

        for daemon in self.model.get_daemons():
            name = DISPLAY_NAMES.get(daemon, daemon)
            status_text, status_style = self.model.get_daemon_status(daemon)

            #radio = urwid.RadioButton(group, '', on_state_change=self.select_daemon, user_data=daemon)
            #self.daemon_radios.append(radio)
            #x = urwid.Columns()
            row = urwid.Columns([
                (urwid.RadioButton(group, '', on_state_change=self.select_daemon, user_data=daemon)),
                (urwid.AttrMap(urwid.Text(name), 'bold')),
                (urwid.Text((status_style, status_text)))
            ])
            body.append(urwid.AttrMap(row, None, focus_map='reversed'))

        body.append(urwid.Divider())
        body.append(urwid.Button("More Info", on_press=self.show_component_info))
        body.append(urwid.Button("Exit", on_press=lambda b: exit(0)))
        return urwid.ListBox(urwid.SimpleFocusListWalker(body))

    def build_main_frame(self):
        left_panel = urwid.LineBox(
            self.build_daemon_list(),
            title="Components",
            title_align="left",
            title_attr="title"
        )

        columns = urwid.Columns(
            [
                ('weight', 1, left_panel),
                ('weight', 2, urwid.Filler(self.right_panel, valign='top'))
            ],
            dividechars=2
        )
        return columns

    def select_daemon(self, radio, new_state, daemon):
        if new_state:
            self.selected_daemon = daemon

    # The main screen shows this content
    def show_component_info(self, button):
        self.right_panel = urwid.Text(('bold', "COMPONENT INFO"))
        self.main_loop.widget = self.build_main_frame()

    def exit_on_q(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()

    def run(self):
        self.main_loop.run()


if __name__ == '__main__':
    Db4eTui().run()
