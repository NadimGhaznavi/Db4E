"""
Widgets/NavPane.py

Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0
"""
from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple
import time

from textual.reactive import reactive
from textual.widgets import Label, Tree
from textual.app import ComposeResult
from textual.containers import Container, Vertical, ScrollableContainer

from db4e.Modules.Helper import get_component_value, worst_status
from db4e.Messages.NavLeafSelected import NavLeafSelected
from db4e.Messages.Db4eMsg import Db4eMsg
from db4e.Modules.OpsMgr import OpsMgr
from db4e.Modules.ConfigMgr import Config
from db4e.Modules.HealthMgr import HealthMgr
from db4e.Constants.Fields import (
    REMOTE_FIELD, DB4E_FIELD, DONATIONS_FIELD, ERROR_FIELD, GOOD_FIELD,
    DATA_FIELD, MONEROD_REMOTE_FIELD, P2POOL_REMOTE_FIELD, INITIAL_SETUP_PROCEED_FIELD,
    INSTANCE_FIELD, MONEROD_FIELD, NEW_FIELD, P2POOL_FIELD, GET_INITIAL_REC_FIELD,
    ELEMENT_TYPE_FIELD, TO_METHOD_FIELD, TO_MODULE_FIELD, INSTALL_MGR_FIELD,
    OPS_MGR_FIELD, SET_PANE_FIELD, GET_NEW_REC_FIELD, GET_REC_FIELD,
    UNKNOWN_FIELD, NAME_FIELD, PANE_MGR_FIELD, WARN_FIELD, XMRIG_FIELD)
from db4e.Constants.Labels import (
    DB4E_LABEL, DEPLOYMENTS_LABEL, DONATIONS_LABEL, INITIAL_SETUP_LABEL,
    MONEROD_SHORT_LABEL, NEW_LABEL, P2POOL_SHORT_LABEL, XMRIG_SHORT_LABEL)
from db4e.Constants.Panes import (
    MONEROD_TYPE_PANE, P2POOL_TYPE_PANE, DONATIONS_PANE, XMRIG_PANE,
    INITIAL_SETUP_PANE)

# Icon dictionary keys
CORE = 'CORE'
DEPL = 'DEPL'
GIFT = 'GIFT'
MON = 'MON'
NEW = 'NEW'
P2P = 'P2P'
SETUP = 'SETUP'
XMR = 'XMR'

ICON = {
    CORE: '📡 ',
    DEPL: '💻 ',
    GIFT: '🎉 ',
    MON: '🌿 ',
    NEW: '🔧 ',
    P2P: '🌊 ',
    SETUP: '⚙️ ',
    XMR: '⛏️  '
}

STATE_ICON = {
    GOOD_FIELD: '🟢 ',
    WARN_FIELD: '🟡 ',
    ERROR_FIELD: '🔴 ',
    UNKNOWN_FIELD: '⚪ ',
}

@dataclass
class NavItem:
    label: str
    field: str
    icon: str

    def __str__(self):
        return self.icon + self.label

class NavPane(Container):

    def __init__(self, config: Config, ops_mgr: OpsMgr):
        super().__init__()
        self.ops_mgr = ops_mgr
        self.health_mgr = HealthMgr()
        self._initialized = False

        # Create the Deployments tree
        self.depls = Tree(ICON[DEPL] + DEPLOYMENTS_LABEL, id="tree_deployments")
        self.depls.guide_depth = 3
        self.depls.root.expand()

        # Setup the navpane cache so we don't hammer the DB
        self._cached_deployments = []
        self._cache_time = 0
        self._cache_ttl = 1  # seconds

        # Current state data from Mongo
        self.monerod_recs = None
        self.p2pool_recs = None
        self.xmrig_recs = None

        # Configure services with their health check handlers
        self.services = [
            (MONEROD_FIELD, ICON[MON], MONEROD_SHORT_LABEL),
            (P2POOL_FIELD, ICON[P2P], P2POOL_SHORT_LABEL),
            (XMRIG_FIELD, ICON[XMR], XMRIG_SHORT_LABEL),
        ]

        self.refresh_nav_pane()

    def check_initialized(self):        
        self._initialized = self.ops_mgr.is_depl_initialized()
        return self._initialized

    def compose(self) -> ComposeResult:
        yield Vertical(ScrollableContainer(self.depls, id="navpane"))

    def flush_cache(self):
        self.get_cached_deployments()
        self._cache_time = time.time()
        self.refresh_nav_pane()

    def get_cached_deployments(self):
        now = time.time()
        if now - self._cache_time > self._cache_ttl:
            self._cached_deployments = self.ops_mgr.get_deployments()
            
            # Create a lookup map by ID for easy dependency resolution
            deployment_map = {dep['_id']: dep for dep in self._cached_deployments}
            
            # Track which deployments have been checked
            checked = set()
            
            def check_deployment_with_dependencies(deployment):
                dep_id = deployment['_id']
                if dep_id in checked:
                    return deployment_map[dep_id]
                
                # For XMRig, find and check its parent P2Pool first
                if deployment.get('element_type') == 'xmrig':
                    parent_id = None
                    for component in deployment.get('components', []):
                        if component.get('field') == 'parent_id':
                            parent_id = component.get('value')
                            break
                    
                    if parent_id and parent_id in deployment_map:
                        # Recursively check the parent P2Pool first
                        parent_deployment = check_deployment_with_dependencies(deployment_map[parent_id])
                        # Pass the checked parent to XMRig health check
                        checked_deployment = self.health_mgr.check(deployment, parent_deployment)
                    else:
                        # No parent found - check without parent
                        checked_deployment = self.health_mgr.check(deployment, None)
                else:
                    # For non-XMRig deployments, check normally
                    checked_deployment = self.health_mgr.check(deployment)
                
                # Calculate status from health_msgs
                if 'health_msgs' in checked_deployment and checked_deployment['health_msgs']:
                    checked_deployment['status'] = worst_status(checked_deployment['health_msgs'])
                else:
                    checked_deployment['status'] = 'unknown'
                
                # Update in the map and mark as checked
                deployment_map[dep_id] = checked_deployment
                checked.add(dep_id)
                return checked_deployment
            
            # Check all deployments (dependencies will be resolved automatically)
            for i, deployment in enumerate(self._cached_deployments):
                self._cached_deployments[i] = check_deployment_with_dependencies(deployment)
            
            self._cache_time = now
        
        return self._cached_deployments
    
    def is_initialized(self) -> bool:
        #print(f"NavPane:is_initialized(): {self._initialized}")
        return self._initialized

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        if not event.node.children and event.node.parent:
            leaf_item: NavItem = event.node.data
            parent_item: NavItem = event.node.parent.data
            #print(f"NavPane:on_tree_node_selected(): leaf_item ({leaf_item}), parent_item ({parent_item})")

            # Initial Setup
            if INITIAL_SETUP_LABEL in leaf_item.label:
                #print(f"NavPane:on_tree_node_selected(): {INITIAL_SETUP_LABEL}")
                rec = self.ops_mgr.get_deployment(DB4E_FIELD)
                form_data = {
                    ELEMENT_TYPE_FIELD: DB4E_FIELD,
                    TO_MODULE_FIELD: INSTALL_MGR_FIELD,
                    TO_METHOD_FIELD: INITIAL_SETUP_PROCEED_FIELD,
                }
                self.post_message(Db4eMsg(self, form_data=form_data))

            # View/Update Db4E Core
            elif DB4E_LABEL in leaf_item.label:
                #print(f"NavPane:on_tree_node_selected(): {DB4E_LABEL}")
                form_data = {
                    ELEMENT_TYPE_FIELD: DB4E_FIELD,
                    TO_MODULE_FIELD: OPS_MGR_FIELD,
                    TO_METHOD_FIELD: GET_REC_FIELD,
                }
                self.post_message(Db4eMsg(self, form_data=form_data))

            # New Monero (remote) deployment
            elif NEW_LABEL in leaf_item.label and MONEROD_SHORT_LABEL in parent_item.label:
                #print(f"NavPane:on_tree_node_selected(): {MONEROD_SHORT_LABEL}/{NEW_LABEL}")
                form_data = {
                    ELEMENT_TYPE_FIELD: MONEROD_FIELD,
                    TO_MODULE_FIELD: PANE_MGR_FIELD,
                    TO_METHOD_FIELD: SET_PANE_FIELD,
                    NAME_FIELD: MONEROD_TYPE_PANE,
                }
                self.post_message(Db4eMsg(self, form_data=form_data))

            # New P2Pool (remote) deployment
            elif NEW_LABEL in leaf_item.label and P2POOL_SHORT_LABEL in parent_item.label:
                #print(f"NavPane:on_tree_node_selected(): {P2POOL_SHORT_LABEL}/{NEW_LABEL}")
                form_data = {
                    ELEMENT_TYPE_FIELD: P2POOL_FIELD,
                    TO_MODULE_FIELD: PANE_MGR_FIELD,
                    TO_METHOD_FIELD: SET_PANE_FIELD,
                    NAME_FIELD: P2POOL_TYPE_PANE,
                }
                self.post_message(Db4eMsg(self, form_data=form_data))

            # New XMRig deployment
            elif NEW_LABEL in leaf_item.label and XMRIG_SHORT_LABEL in parent_item.label:
                #print(f"NavPane:on_tree_node_selected(): {XMRIG_SHORT_LABEL}/{NEW_LABEL}")
                form_data = {
                    ELEMENT_TYPE_FIELD: XMRIG_FIELD,
                    TO_MODULE_FIELD: OPS_MGR_FIELD,
                    TO_METHOD_FIELD: GET_NEW_REC_FIELD,
                }
                self.post_message(Db4eMsg(self, form_data=form_data))

            elif parent_item:

                # View/Update a Monero deployment
                if MONEROD_SHORT_LABEL in parent_item.label:
                    #print(f"NavPane:on_tree_node_selected(): {MONEROD_SHORT_LABEL}/{leaf_item.label}")
                    record = self.ops_mgr.get_deployment(elem_type=MONEROD_FIELD, instance=leaf_item.field)
                    remote = get_component_value(record, REMOTE_FIELD)
                    if remote:
                        form_data = {
                            ELEMENT_TYPE_FIELD: MONEROD_REMOTE_FIELD,
                            TO_MODULE_FIELD: OPS_MGR_FIELD,
                            TO_METHOD_FIELD: GET_REC_FIELD,
                            INSTANCE_FIELD: leaf_item.field
                        }
                    else:
                        form_data = {
                            ELEMENT_TYPE_FIELD: MONEROD_FIELD,
                            TO_MODULE_FIELD: OPS_MGR_FIELD,
                            TO_METHOD_FIELD: GET_REC_FIELD,
                            INSTANCE_FIELD: leaf_item.field
                        }
                    self.post_message(Db4eMsg(self, form_data=form_data))

                # View/Update a P2Pool deployment
                elif P2POOL_SHORT_LABEL in parent_item.label:
                    #print(f"NavPane:on_tree_node_selected(): {P2POOL_SHORT_LABEL}/{leaf_item.label}")
                    record = self.ops_mgr.get_deployment(elem_type=P2POOL_FIELD, instance=leaf_item.field)
                    remote = get_component_value(record, REMOTE_FIELD)
                    if remote:
                        form_data = {
                            ELEMENT_TYPE_FIELD: P2POOL_REMOTE_FIELD,
                            TO_MODULE_FIELD: OPS_MGR_FIELD,
                            TO_METHOD_FIELD: GET_REC_FIELD,
                            INSTANCE_FIELD: leaf_item.field
                        }
                    else:
                        form_data = {
                            ELEMENT_TYPE_FIELD: P2POOL_FIELD,
                            TO_MODULE_FIELD: OPS_MGR_FIELD,
                            TO_METHOD_FIELD: GET_REC_FIELD,
                            INSTANCE_FIELD: leaf_item.field
                        }
                    self.post_message(Db4eMsg(self, form_data=form_data))

                # View/Update a XMRig deployment
                elif XMRIG_SHORT_LABEL in parent_item.label:
                    #print(f"NavPane:on_tree_node_selected(): {XMRIG_SHORT_LABEL}/{leaf_item.label}")
                    form_data = {
                        ELEMENT_TYPE_FIELD: XMRIG_FIELD,
                        TO_MODULE_FIELD: OPS_MGR_FIELD,
                        TO_METHOD_FIELD: GET_REC_FIELD,
                        INSTANCE_FIELD: leaf_item.field
                    }
                    self.post_message(Db4eMsg(self, form_data=form_data))

            # Donations
            elif DONATIONS_LABEL in leaf_item.label:
                #print(f"NavPane:on_tree_node_selected(): {DONATIONS_LABEL}")
                form_data = {
                    ELEMENT_TYPE_FIELD: DONATIONS_FIELD,
                    TO_MODULE_FIELD: PANE_MGR_FIELD,
                    TO_METHOD_FIELD: SET_PANE_FIELD,
                    NAME_FIELD: DONATIONS_PANE,
                }
                self.post_message(Db4eMsg(self, form_data=form_data))


            elif isinstance(leaf_item, NavItem) and isinstance(parent_item, NavItem):
                self.post_message(NavLeafSelected(
                    self,
                    parent=parent_item.field, 
                    leaf=leaf_item.field
                ))
                event.stop()

    def refresh_nav_pane(self) -> None:
        self.check_initialized()
        self.depls.root.remove_children()
        
        # Db4E Core root node
        core_item = NavItem(DB4E_LABEL, DB4E_FIELD, ICON[CORE])
        setup_item = NavItem(INITIAL_SETUP_LABEL, DB4E_FIELD, ICON[SETUP])
        
        if not self.is_initialized():
            # Add Donations link
            donate_item = NavItem(DONATIONS_LABEL, DONATIONS_FIELD, ICON[GIFT])
            self.depls.root.add_leaf(str(setup_item), data=setup_item)
            self.depls.root.add_leaf(str(donate_item), data=donate_item)
            return
        
        self.depls.root.add_leaf(str(core_item), data=core_item)
        all_recs = self.get_cached_deployments()  # Cached call
        
        # Precompute <New> label
        new_leaf = NavItem(NEW_LABEL, NEW_FIELD, ICON[NEW])
        
        # Map element_types to service categories
        service_mappings = {
            MONEROD_FIELD: ['monerod', 'monerod_remote'],
            P2POOL_FIELD: ['p2pool', 'p2pool_remote'], 
            XMRIG_FIELD: ['xmrig']
        }
        
        # Group deployments by service category
        grouped: Dict[str, List[dict]] = {field: [] for field, _, _ in self.services}
        for rec in all_recs:
            element_type = rec.get('element_type')
            # Find which service category this element_type belongs to
            for service_field, element_types in service_mappings.items():
                if element_type in element_types:
                    grouped[service_field].append(rec)
                    break
        
        for field, icon, label in self.services:
            service_item = NavItem(label, field, icon)
            parent = self.depls.root.add(str(service_item), data=service_item, expand=True)
            for rec in grouped.get(field, []):
                # Use helper function to get instance name from components
                instance = get_component_value(rec, INSTANCE_FIELD) or rec.get('name', 'Unknown')
                state = rec.get('status')
                #print(f"NavPane:refresh_nav_pane(): instance: {instance}, state: {repr(state)})")
                instance_item = NavItem(instance, instance, STATE_ICON.get(state, ""))
                parent.add_leaf(str(instance_item), data=instance_item)
            
            # Add <New> if valid (i.e., P2Pool must exist before XMRIG)
            if field != XMRIG_FIELD or grouped.get(P2POOL_FIELD):
                parent.add_leaf(str(new_leaf), data=new_leaf)
        
        # Add Donations link
        donate_item = NavItem(DONATIONS_LABEL, DONATIONS_FIELD, ICON[GIFT])
        self.depls.root.add_leaf(str(donate_item), data=donate_item)
