# Properties for Edtior Dialogs #

These properties can be specified in the command class for the command and properties
in order to allow the editor classes to layout and provide appropriate input input components.
The data can be maintained in the `AbstractCommand`.

```
# Dictionary of string properties to describe command metadata.
command_metadata = {}

# Dictionary of string properties to describe command parameters.
parameter_metadata = {}
```

| **Command Property** | **Description** | **Default** |
|----------------------|-----------------|-------------|
| `Description`        | Description of the command to display at the top of the command dialog. Can this be HTML with embedded link? | Command name. |
| `EditorType`         | What type of editor to use, `Simple` or `Tabbed` (maybe make this an enumeration). |

| **Parameter Property** | **Description** | **Default** |
|------------------------|-----------------|-------------|
| `ParameterName.Group`  | The group (tab) used to group parameters, such as `Input`. | No group used - use simple editor. |
| `ParameterName.Description` | The description to be shown on the right-side of the editor. | No description is shown. |
| `ParameterName.Label` | The label to be shown to the left` of the component. | Parameter name. |
| `ParameterName.Tooltip` | The tooltip to be shown when moused over the input component. | No tooltip is shown. |
| `ParameterName.Required` | Indicate whether required:  `Required`, `Optional`, or maybe something more complex. | Must be specified. |
| `ParameterName.Values` | Indicate a list of values to show in choices, may need a way to dynamically populate (lambda?). |
| `ParameterName.DefaultValue` | The default value as a string, as if the user entered into the component, to be shown in the description. |
| `ParameterName.FileSelectorType` | Indicate the type of selector as enumeration `Read`, `Write`.  Will result in `...` button to browse for fall. |
| `ParameterName.?` | Need some way to indicate default file extension, recognized extensions and descriptions | |
| `ParameterName.?` | Perhaps need a way to set the dimention of a text field or text area. Dialogs are kind of ugly when text fields span the entire width.  Maybe use the concept of number of columns? | |

The parameter name needs to be part of the property to ensure that the relationships are describe in flat form.
The `command_util` module can be updated with methods to extract from the metadata the dictionary value,
for example to get the commands in the proper order.

The format of the description should be `Required - Description (default=DefaultValue)`,
with intelligence to handle None and empty strings.

The validation for the component should be able to occur using exising command editor features.
This can validate whether input is a number, etc.
It may be possible to use the metadata to automatically implement validators but that does not need to happen now.

Need to try implementing the editing features with a simple command and then evaluate more complex editor/layout properties.
