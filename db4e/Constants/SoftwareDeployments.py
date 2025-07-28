# Constants/SoftwareDeploymentd

from db4e.Constants.Core import NAME_FIELD

CLIENT_DEPENDENCY_FIELD = "clientDependency"
CONSTRAINT_FIELD = "constraint"
DESIGN_PACKAGE_FIELD = "designPackage"
IMPORTED_ELEMENT_FIELD = "importedElement"
IMPORTER_FIELD = "importer"



# Dummy placeholders
placeholder = {}

Component_Template = placeholder
Model_Element_Template = placeholder
Package_Template = placeholder

Model_Element_Template = {
    NAME_FIELD: "",


}

Package_Template = {
    IMPORTED_ELEMENT_FIELD:Model_Element_Template,
}

Component_Template = {
    DESIGN_PACKAGE_FIELD: Package_Template,
}