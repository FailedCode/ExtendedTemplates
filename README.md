
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

| Key                   | Type          | Description |
| :-------------------- | :------------ | :---------- |
| `name`                | string        | Will be shown when selecting a snippet. |
| `description`         | string        | Explain here what this is used for. Will be shown when selecting a snippet.|
| `vars`                | dictionary    | Pairs of variable name and variable value. |
| `files_and_folders`   | array         | Lists folders (ending with a slash) and files (no slash). May contain variables. |
| `content`             | dictionary    | Pairs of name and string templates. May contain variables. |

#### `files_and_folders`
Filepaths may be appended with a pipe "|" character, followed by a path to a template file or a named content, used as a template for the first file. Multiple templates can be used (separated by more pipes). The path is relative to the snippet file. Named content must be enclosed in angle brackets "<name>". The values will be appended to the file.  
Already existing files will not be altered.

#### `content`
If you need only a very small template and don't want to clutter your system with tiny files, you can define content within the snippet file.

## Variables
The user gets promptet to input variable values if their value is the same as their key. They may be set in the snippet file or the settings.  
Occurences of `${var_name}` will be replaced.

### Special variables
These variables are filled on runtime with the current date/time:

| Variable     | Format               | Example Value |
| :----------- | :------------------- | :------------ |
| `_timestamp` | `%Y-%m-%dT%H:%M:%SZ` | `2015-09-27T16:59:15Z` |
| `_datetime`  | `%Y-%m-%d %H:%M`     | `2015-09-27 16:59` |
| `_date`      | `%Y-%m-%d`           | `2015-09-27` |
| `_time`      | `%H:%M`              | `16:59` |

### Sublime variables
These variables are provided by Sublime text:  
`packages`, `platform`, `file`, `file_path`, `file_name`, `file_base_name`, `file_extension`, `folder`, `project`, `project_path`, `project_name`, `project_base_name`, `project_extension`  
See also [API reference](https://www.sublimetext.com/docs/3/api_reference.html)

### Order of variable substitution
1. Sublime Text variables
2. Variables set in the settings file
3. Variables set in snippet file
4. Special variables

So, you could override `project_path` in your settings file or set `author_name` in the snippet file to the value `author_name` to prompt the user.

## Examples

#### Snippet
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
#### Creates

| Path             | Description     |
| :--------------- | :-------------- |
| `base/`          | Empty Directory |
| `base/foobar/`   | Empty Directory |
| `base/readme.md` | Empty File      |

#### Snippet
``` json
{
	"name": "HTML",
	"description": "Small HTML project",
	"files_and_folders": [
		"css/style.css|<banner>",
		"js/script.js|<banner>|<js-ready>",
		"index.html|html/index.html"
	],
	"content": {
		"banner": "/* Created at ${_datetime} by ${author_name} */\n",
		"js-ready": "\n$(function() {\n\n});\n"
	}
}
```
#### Creates

| Path            | Description |
| :-------------- | :---------- |
| `css/`          | Empty Directory |
| `css/style.css` | File with the `banner` content |
| `js/`           | Empty Directory |
| `js/script.js`  | File with the `banner` and `js-ready` content |
| `index.html`    | File with the contents of the file `html/index.html` (relative to the json file) |

## Inspired by
https://github.com/bit101/STProjectMaker

## License
See "UNLICENSE" file.
