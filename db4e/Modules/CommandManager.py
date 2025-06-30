# db4e/Modules/ArgumentParser.py

#   Database 4 Everything
#   Author: Nadim-Daniel Ghaznavi 
#   Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
#   License: GPL 3.0import argparse
 
class CommandManager:

    def __init__(self):

        self.command_keys = {
            "db4e_app": {
                "Commands": {
                    "q": {
                        "human_key": "q",
                        "description": "Quit"
                        },
                    },
                }
        }

        # These are keys that we let go through no matter what
        self.exclude_keys = [
            "up",
            "down",
            "left",
            "right",
            "pageup",
            "pagedown",
            "home",
            "end",
            "tab",
            "enter",
            "grave_accent",
            "q",
            "question_mark",
            "plus",
            "minus",
            "equals_sign",
            "ctrl+a",
            "ctrl+d",
        ]

    def get_commands(self, context="db4e_app"):
        return self.command_keys.get(key, {}).get("Commands")
    


    # db4e_app