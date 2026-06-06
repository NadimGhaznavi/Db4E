"""
widgets/NavPaneState.py

Database 4 Everything
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""

from dataclasses import dataclass
from textual.widgets.tree import TreeNode


@dataclass
class NavPaneState:
    """Holds all mutable state for the NavPane widget.

    Lifecycle flags
    ---------------
    db4e_installed        : True once db4e has been installed on this host.
    depls_branches_added  : True once the main deployment subtrees have been
                            added to the Textual Tree (prevents double-adding).
    initial_branches_added: True while the pre-install "Initial Setup /
                            Donations" leaves are showing, so they can be
                            removed cleanly when installation completes.
    sudo_failed           : True when the sudo pre-flight check fails; causes
                            the nav pane to show only the Donations leaf.

    Tree-node references
    --------------------
    Set inside refresh_nav_pane() after the branches are first created.
    All default to None so callers can guard with ``if self.state.monerod_tree``.
    """

    # --- Lifecycle flags ---
    db4e_installed: bool = False
    depls_branches_added: bool = False
    initial_branches_added: bool = False
    sudo_failed: bool = False

    # --- Live tree-node references (populated by refresh_nav_pane) ---
    monerod_tree: TreeNode | None = None
    monerod_remote_tree: TreeNode | None = None
    p2pool_tree: TreeNode | None = None
    p2pool_remote_tree: TreeNode | None = None
    xmrig_tree: TreeNode | None = None
    xmrig_remote_tree: TreeNode | None = None
    chain: TreeNode | None = None
