# db4e/Messages/InstallResult.py
#
#    Database 4 Everything
#    Author: Nadim-Daniel Ghaznavi
#    Copyright (c) 2024-2025 NadimGhaznavi <https://github.com/NadimGhaznavi/db4e>
#    License: GPL 3.0
#
# Usage example:
#     self.post_message(RefreshNavPane(self)

from textual.widget import Widget
from textual.message import Message


class InstallResult(Message):
    """
    Message signaling that the navigation pane should refresh.
    """

    def __init__(self, sender: Widget, result: bool) -> None:
        """
        Initialize the refresh message.

        :param sender: Widget that emitted the refresh request.
        :type sender: Widget
        :return: None
        :rtype: None
        """
        super().__init__()
        self.sender = sender
        self.install_successful = result
