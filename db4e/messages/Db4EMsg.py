# db4e/Messages/Db4EMsg.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
#    License: GPL 3.0

from textual.widget import Widget
from textual.message import Message


class Db4EMsg(Message):
    """
    Message wrapper for passing form data from Textual widgets.
    """

    def __init__(self, sender: Widget, form_data: dict) -> None:
        """
        Initialize the message with sender and form payload.

        :param sender: Textual widget that emitted the message.
        :type sender: Widget
        :param form_data: Form payload data.
        :type form_data: dict
        """
        super().__init__()
        self.form_data = form_data
