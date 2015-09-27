
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

### Examples
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
Creates:

| Path | Description |
| :--- | :---------- |
| `base/` | Empty Directory |
| `base/foobar/` | Empty Directory |
| `base/readme.md` | Empty File |


``` json
{
	"name": "HTML",
	"description": "Small HTML project",
	"vars": {},
	"files_and_folders": [
		"css/style.css",
		"js/script.js",
		"index.html|html/index.html"
	]
}
```
Creates:

| Path | Description |
| :--- | :---------- |
| `css/` | Empty Directory |
| `css/style.css` | Empty File |
| `js/` | Empty Directory |
| `js/script.js` | Empty File |
| `index.html` | File with the contents of the file `html/index.html` (relative to the json file) |


## Variables
The user gets promptet to input variable values if they are not set in the snippet or the settings.
Occurences of `${<var_name>}` will be replaced.

### Special vars
These variables are filled on runtime with the current date/time:

| Variable | Format | Example Value |
| :------- | :----- | :------------ |
| `_timestamp` | `%Y-%m-%dT%H:%M:%SZ` | `2015-09-27T16:59:15Z` |
| `_datetime` | `%Y-%m-%d %H:%M` | `2015-09-27 16:59` |
| `_date` | `%Y-%m-%d` | `2015-09-27` |
| `_time` | `%H:%M` | `16:59` |

## Inspired by
https://github.com/bit101/STProjectMaker

## License
See "UNLICENSE" file.
