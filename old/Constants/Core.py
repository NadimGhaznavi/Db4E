# Core Constants

CHANGEABLE_FIELD = "changeable"
NAME_FIELD = "name"

# Placeholder
Placeholder = {}


# Dummy placeholder to avoid circular import issues
Tagged_Value_Template = Placeholder
Classifier_Template = Placeholder
Dependency_Template = Placeholder
Feature_Template = Placeholder
Model_Element_Template = Placeholder
Namespace_Template = Placeholder
Package_Template = Placeholder

ModelElement_Template = {
    NAME_FIELD: "",
    "clientDependency": [],
    "constraint": [],
    "importer": Package_Template,
    "namespace": Namespace_Template,
    "taggedValue": [],
}

Dependency_Template ={
    "parentIds": [Model_Element_Template],
    "kind": "",
    "client": Model_Element_Template,
    "supplier": Model_Element_Template
}

Feature_Template = {
    "ownerScope": "",
    "owner": Classifier_Template,
}

Namespace_Template = {
    "PARENT_IDS": [Model_Element_Template],
    "OWNED_ELEMENT": [],
}

Tagged_Value_Template = {
    "TAG": "",
    "VALUE": "",
    "MODEL_ELEMENT": Model_Element_Template,
}

Classifier_Template = {
    "IS_ABSTRACT": bool,
    "IS_ORDERED": True,
    "FEATURE": [],
    "STRUCTURAL_FEATURE": [],
    "MODEL_ELEMENT": [Model_Element_Template]
}

Package_Template = {
    "PARENT_IDS": [Namespace_Template],
    "IMPORTED_ELEMENT": Model_Element_Template
}

Subsystem_Template = {
    "PARENT_IDS": [Classifier_Template, Package_Template]
}