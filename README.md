
# ExtendedTemplates
This is a plugin for [Sublime Text 3](http://www.sublimetext.com/).
It adds the ability to create multiple files and folders (defined in json snippet files) from the sidebar menu.

## Install
Download / Clone to `Sublime Text 3\Data\Packages`

## Settings
Like most plugins, the settings are added to the menu at `Preferences / Package Settings / Extended Templates`
Make sure to define the "vars" block in your user settings.

## Snippets
The default templates are located in the plugin subfolder "templates".
Every json file should contain these values:
`name` *string* Will be shown when selecting a snippet.
`description` *string* Explain here what this is used for. Will be shown when selecting a snippet.
`vars` *dictionary* **key** variable name **value** variable value
`files_and_folders` *array* Lists folders (ending with a slash) and files (no slash).
Files and Folders may contain variables.
Files may be appended with a pipe "|" character, followed by a path to a second file, used as a
template for the first file. The Template file may contain variables. The path is relative to
the snippet file.

### Example
``` json
{
	"name": "Test",
	"description": "Simple example for a snippet",
	"vars": {
		"dir": "foobar"
	},
	"files_and_folders": [
		"base/${dir}/",
		"base/readme.md"
	]
}
```

## Variables
The user gets promptet to input variable values if they are not set in the snippet or the settings.
Occurences of `${<var_name>}` will be replaced.

## Inspired by
https://github.com/bit101/STProjectMaker

## License
See "UNLICENSE" file.
