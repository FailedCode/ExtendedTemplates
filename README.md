
# ExtendedTemplates
This is a plugin for [Sublime Text 3](http://www.sublimetext.com/).  
It adds the ability to create multiple files and folders (defined in json snippet files) from the sidebar menu.

## Install
Download / Clone to `Sublime Text 3\Data\Packages`

## Settings
Like most plugins, the settings are added to the menu at `Preferences / Package Settings / Extended Templates`  
Make sure to define the "vars" block in your user settings.  
Read the default settings file for detailed information.

## Snippets
The default snippets are located in the plugin subfolder "templates" (the folders in the settings are searched recursively) and must end with `.def.json`. You can place your own in the `User/ExtendedTemplates/templates/` directory. 
Every json file can contain these values:

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
All occurences of `${var_name}` will be found in the snippet file and the template files.  
Variables may be set in the snippet file or the settings.  

### Methods to set variables

#### Example `text`
```
	"vars": {
		"version": "v1.0.5",
		"name": "name",
	}
```
The user won't be promptet for `version`, `${version}` will replaced with `v1.0.5`.  
The user will be promptet to enter a string for `name`, `${name}` will replaced with the entered string. It makes sense to do this only if you want to override a variable with some user input, since the user will be promptet for every variable used but not explicitly set.

#### Example `dict`
```
	"vars": {
		"food": [
			{"value": "cake",  "text": "Sweet and tasty!"},
			{"value": "bacon", "text": "Salty and delicous!"},
			{"value": "curry", "text": "Hot, hot and hot!"}
		]
	}
```
The user will ne promptet for `food`, `${food}` will replaced with one of these: `cake`, `bacon`, `curry` or an empty String.

#### Example `list`
```
	"vars": {
		"food": [
			["cake",  "Sweet and tasty!"],
			["bacon", "Salty and delicous!"],
			["curry", "Hot, hot and hot!"]
		]
	}
```
Exactly the same as the example above!

### Special variables
These variables are filled on runtime with the current date/time:

| Variable     | Format               | Example Value          |
| :----------- | :------------------- | :--------------------- |
| `_timestamp` | `%Y-%m-%dT%H:%M:%SZ` | `2015-09-27T16:59:15Z` |
| `_datetime`  | `%Y-%m-%d %H:%M`     | `2015-09-27 16:59`     |
| `_date`      | `%Y-%m-%d`           | `2015-09-27`           |
| `_time`      | `%H:%M`              | `16:59`                |
| `_year`      | `%Y`                 | `2015`                 |
| `_month`     | `%m`                 | `09`                   |
| `_day`       | `%d`                 | `27`                   |

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

### Variable Modification
There are some options available to modify values before they are inserted. At this time is it not possible to combine modifiers.

| Modifier | Usage             | Effect           |
| :------- | :---------------- |:---------------- |
| *none*   | `${var}`          | `this IS a teSt` |
| upper    | `${var|upper}`    | `THIS IS A TEST` |
| lower    | `${var|lower}`    | `this is a test` |
| title    | `${var|title}`    | `This Is A Test` |
| capital  | `${var|capital}`  | `This IS a teSt` |
| camel    | `${var|camel}`    | `ThisIsATest`    |
| snake    | `${var|snake}`    | `this_is_a_test` |
| constant | `${var|constant}` | `THIS_IS_A_TEST` |


## Examples

#### Snippet `python.json`
``` json
{
	"name": "Python Module",
	"description": "Empty python Module",
	"files_and_folders": [
		"${module_name}/__init__.py"
	]
}
```
#### Creates

| Path                      | Description     |
| :------------------------ | :-------------- |
| `module_name/`            | Empty directory |
| `module_name/__init__.py` | Empty file      |

#### Snippet `phpclass.json`
``` json
{
	"name": "php class",
	"description": "Add a php class",
	"files_and_folders": [
		"${name}Class.php|php/class.php"
	]
}
```
#### Creates

| Path             | Description     |
| :--------------- | :-------------- |
| `nameClass.php`  | File with the contents of the file `php/class.php` (relative to the json file) |

#### Snippet `html.json`
``` json
{
	"name": "HTML",
	"description": "Small HTML project",
	"vars": {
		"version": "-html5"
	},
	"files_and_folders": [
		"css/style.css|<banner>",
		"js/script.js|<banner>|<js-ready>",
		"index.html|html/index${version}.html"
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
| `css/`          | Empty directory |
| `css/style.css` | File with the `banner` content |
| `js/`           | Empty directory |
| `js/script.js`  | File with the `banner` and `js-ready` content |
| `index.html`    | File with the contents of the file `html/index-html5.html` |

#### Snippet `jquery.json`
``` json
{
	"name": "jQuery",
	"description": "Select a jQuery version",
	"vars": {
		"version": [
			{"value": "1.11.3", "text": "jQuery 1.x"},
			{"value": "2.1.4",  "text": "jQuery 2.x"},
			{"value": "3.0.0",  "text": "jQuery 3.x"}
		],
		"min": [
			[".min", "use compressed source"],
			["",     "use uncompressed developmend source"]
		]
	},
	"files_and_folders": [
		"jquery.js|js/jquery-${version}${min}.js"
	]
}
```
#### Creates

| Path            | Description |
| :-------------- | :---------- |
| `jquery.js`     | Copys the content from `js/jquery-1.11.3.min.js` if the first options are selected **or** from `js/jquery-.js` if the User hits Escape in every case. |

## Inspired by
https://github.com/bit101/STProjectMaker

## License
See "UNLICENSE" file.
