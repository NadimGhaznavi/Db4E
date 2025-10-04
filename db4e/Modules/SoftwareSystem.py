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

from db4e.Constants.DStatus import DStatus
from db4e.Constants.DField import DField
from db4e.Constants.DLabel import DLabel
from db4e.Constants.DJob import DJob


class SoftwareSystem:
    

    def __init__(self):
        self._elem_type = DField.SOFTWARE_SYSTEM
        self.name = DLabel.SOFTWARE_SYSTEM
        self._object_id = None
        self.components = {}
        self.msgs = []


    def __repr__(self):
        if DField.INSTANCE in self.components:
            return f"{type(self).__name__}({self.components[DField.INSTANCE].value})"
        return f"{type(self).__name__}"


    def add_component(self, comp_key: str, comp_instance):
        self.components[comp_key] = comp_instance


    def elem_type(self):
        return self._elem_type


    def from_rec(self, rec: dict):
        if not self.components:
            raise RuntimeError(
                "SoftwareSystem:from_rec(): Missing 'components' dict in subclass.")


        for component in rec[DField.COMPONENTS]:
            field_name = component[DField.FIELD]
            if field_name in self.components:
                self.components[field_name].value = component[DField.VALUE]
            else:
                raise ValueError(f"SoftwareSystem:from_rec(): {rec[DField.ELEMENT_TYPE]} - Unknown component field: {field_name}")
        self._object_id = rec[DField.OBJECT_ID]
        self._elem_type = rec[DField.ELEMENT_TYPE]


    def id(self, object_id=None):
        if object_id is not None:
            self._object_id = object_id
        return self._object_id


    def msg(self, label: str, status: str, msg: str):
        self.msgs.append({label: {DJob.STATUS: status, DJob.MESSAGE: msg }})


    def pop_msgs(self):
        msgs = self.msgs
        self.msgs = []
        return msgs


    def push_msgs(self, msgs: list):
        self.msgs.extend(msgs)


    def status(self):
        # The status is defined as the worst status message in the self.msgs list.
        #print(f"SoftwareSystem:status(): self.msgs: {self.msgs}")
        if len(self.msgs) == 0:
            return DStatus.UNKNOWN
        worst_status = DStatus.GOOD
        for line_item in self.msgs:
            #print(f"SoftwareSystem:status(): line_item: {line_item}")
            for key in line_item:
                if line_item[key][DJob.STATUS] == DStatus.UNKNOWN:
                    return DStatus.UNKNOWN
                elif line_item[key][DJob.STATUS] == DStatus.ERROR:
                    return DStatus.ERROR
                elif line_item[key][DJob.STATUS] == DStatus.WARN:
                    worst_status = DStatus.WARN
        return worst_status        


    def to_rec(self) -> dict:
        rec = {
            DField.OBJECT_ID: self.id(),
            DField.NAME: self.name,
            DField.ELEMENT_TYPE: self.elem_type(),
            DField.COMPONENTS: [],
        }
        for component in self.components.keys():
            rec[DField.COMPONENTS].append({
                DField.FIELD: component,
                DField.LABEL: self.components[component].label,
                DField.VALUE: self.components[component].value
            })

        return rec
    
    def to_health_rec(self) -> dict:
        rec = {
            DField.OBJECT_ID: self.id(),
            DField.NAME: self.name,
            DField.ELEMENT_TYPE: self.elem_type(),
            DField.COMPONENTS: [],
            DField.MESSAGES: [],
        }
        for component in self.components.keys():
            rec[DField.COMPONENTS].append({
                DField.FIELD: component,
                DField.LABEL: self.components[component].label,
                DField.VALUE: self.components[component].value
            })
        for msg in self.pop_msgs():
            rec[DField.MESSAGES].append(msg)
        return rec