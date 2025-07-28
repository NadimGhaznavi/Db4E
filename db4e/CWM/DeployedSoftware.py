from db4e.Constants.Fields import (
    COMPONENT_FIELD, IP_ADDR_FIELD, INSTALL_DIR_FIELD, PARENT_ID_FIELD)

# Placeholder
Placeholder = {}

## Templates

# Dummy placeholder to avoid circular import issues

Machine_Template = {
    IP_ADDR_FIELD: "",
    "DEPLOYED_COMPONENT": [],
}

Deployed_Component_Template = {
    INSTALL_DIR_FIELD: "",
    COMPONENT_FIELD: None,
    "MACHINE": None,
}

Deployed_Software_System_Template = {
    "SOFTWARE_SYSTEM": None,
    "PARENT_ID_FIELD": Package_Template,
}

Component_Template = {
    "IMPORTER": [],
    "DEPLOYMENT": [],
    "NAMESPACE": None,
}

Software_System_Template = {
    PARENT_ID_FIELD: Subsystem,
}