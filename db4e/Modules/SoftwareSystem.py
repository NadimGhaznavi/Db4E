"""
db4e/Modules/SoftwareSystem.py

    Database 4 Everything
    Author: Nadim-Daniel Ghaznavi 
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/db4e
    License: GPL 3.0

Defines operations that are common to all SoftareSystems instances.

This is a virtual class.
"""

from db4e.Modules.Components import ObjectId
from db4e.Constants.Fields import SOFTWARE_SYSTEM_FIELD
from db4e.Constants.Labels import SOFTWARE_SYSTEM_LABEL
from db4e.Constants.Fields import (
    COMPONENTS_FIELD, ELEMENT_TYPE_FIELD, FIELD_FIELD, LABEL_FIELD, NAME_FIELD,
    VALUE_FIELD, OBJECT_ID_FIELD,
    GOOD_FIELD, WARN_FIELD, ERROR_FIELD, INSTANCE_FIELD)
from db4e.Constants.Jobs import (STATUS_FIELD, MESSAGE_FIELD)


class SoftwareSystem:
    

    def __init__(self):
        self._elem_type = SOFTWARE_SYSTEM_FIELD
        self.name = SOFTWARE_SYSTEM_LABEL
        self._object_id = None
        self.components = {}
        self.msgs = []


    def __repr__(self):
        if INSTANCE_FIELD in self.components:
            return f"{type(self).__name__}({self.components[INSTANCE_FIELD].value})"
        return f"{type(self).__name__}"


    def add_component(self, comp_key: str, comp_instance):
        self.components[comp_key] = comp_instance


    def elem_type(self):
        return self._elem_type


    def from_rec(self, rec: dict):

        if not self.components:
            raise RuntimeError(
                "SoftwareSystem:from_rec(): Missing 'components' dict in subclass.")

        for component in rec[COMPONENTS_FIELD]:
            field_name = component[FIELD_FIELD]
            if field_name in self.components:
                self.components[field_name].value = component[VALUE_FIELD]
            else:
                raise ValueError(f"Unknreturnown component field: {field_name}")
        self._object_id = rec[OBJECT_ID_FIELD]
        self._elem_type = rec[ELEMENT_TYPE_FIELD]


    def id(self):
        return self._object_id


    def msg(self, label: str, status: str, msg: str):
        self.msgs.append({label: {STATUS_FIELD: status, MESSAGE_FIELD: msg }})


    def pop_msgs(self):
        msgs = self.msgs
        self.msgs = []
        return msgs


    def push_msgs(self, msgs: list):
        self.msgs.extend(msgs)


    def status(self):
        # The status is defined as the worst status message in the self.msgs list.
        #print(f"SoftwareSystem:status(): self.msgs: {self.msgs}")
        worst_status = GOOD_FIELD
        for line_item in self.msgs:
            #print(f"SoftwareSystem:status(): line_item: {line_item}")
            for key in line_item:
                if line_item[key][STATUS_FIELD] == ERROR_FIELD:
                    return ERROR_FIELD
                elif line_item[key][STATUS_FIELD] == WARN_FIELD:
                    worst_status = WARN_FIELD
        return worst_status        


    def to_rec(self) -> dict:
        rec = {
            OBJECT_ID_FIELD: self.id(),
            NAME_FIELD: self.name,
            ELEMENT_TYPE_FIELD: self.elem_type(),
            COMPONENTS_FIELD: [],
        }
        for component in self.components.keys():
            rec[COMPONENTS_FIELD].append({
                FIELD_FIELD: component,
                LABEL_FIELD: self.components[component].label,
                VALUE_FIELD: self.components[component].value
            })

        return rec