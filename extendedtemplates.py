import sublime
import sublime_plugin
import os
import json
import re
import functools
import datetime
import shutil


class SnippetFile(object):
    """
        Save all data from json file for later
    """

    def __init__(self, name, description, files_and_folders, content, var, path):
        self.name = name
        self.description = description
        self.files_and_folders = files_and_folders
        self.content = content
        self.vars = var
        self.path = path
        self.dir = os.path.dirname(path)


class ExtendedTemplatesUtility(object):
    """
        Contains some utility functions
    """

    def __init__(self):
        self.plugin_name = 'ExtendedTemplates'
        self.settings_file = self.plugin_name + '.sublime-settings'

    def load_settings(self):
        return sublime.load_settings(self.settings_file)

    def get_plugin_dir(self):
        return os.path.join(sublime.packages_path(), self.plugin_name)

    def resolve_path(self, path, relative_to):
        """
            make a absolute path from the input
            relative_to
        """
        if path.startswith('~'):
            path = os.path.expanduser(path)
        elif path.startswith('/'):
            path = os.path.abspath(path)
        else:
            path = os.path.abspath(os.path.join(relative_to, path))
        return path

    def get_file_content(self, path):
        with open(path, "r") as f:
            content = f.read()
        return content

    def put_file_content(self, path, content):
        with open(path, "a") as f:
            f.write(content)

    def touch_file(self, path):
        with open(path, 'a'):
            os.utime(path, None)

    def merge_dicts(self, *dict_args):
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result

    def merge_lists(self, *list_args):
        result = []
        for l in list_args:
            result = list(set(result + l))
        return result

    def multi_input(self, gen_function, on_done=None):
        """
            Since show_input_panel is an asynchronous
            function, you can not simply use it in a loop.

            gen_function can call yield with two arguments to
            be inserted at gen_function.send.

            It's magic as far as I'm concerned, so thanks Eric
            for the neat example @ http://stackoverflow.com/questions/17507504/pythonic-way-to-manage-multiple-callbacks
        """
        def progress(result):
            try:
                progress.variable_name, progress.initial_value = gen_function.send(result)

                if type(progress.initial_value) is str:
                    sublime.active_window().show_input_panel(
                        progress.variable_name,
                        progress.initial_value,
                        progress, None, None
                    )
                else:
                    items = []
                    for option in progress.initial_value:
                        if type(option) is dict:
                            text = option['text']
                            desc = 'sets var "{0}" to "{1}"'.format(progress.variable_name, option['value'])
                        elif type(option) is list and len(option) > 1:
                            text = option[1]
                            desc = 'sets var "{0}" to "{1}"'.format(progress.variable_name, option[0])
                        items.append([text, desc])
                    sublime.active_window().show_quick_panel(
                        items,
                        progress
                    )

            except StopIteration:
                if hasattr(on_done, '__call__'):
                    on_done()
                pass
        progress(None)


class NewFromTemplateCommand(sublime_plugin.WindowCommand):
    """
        new_from_template Command
    """

    def __init__(self, paths=[], name=""):
        self.window = sublime.active_window()
        self.util = ExtendedTemplatesUtility()
        self.settings = self.util.load_settings()
        self.log_level = self.settings.get('log_level', 'NONE')
        self.log_level_list = {'NONE': 0, 'DEBUG': 25, 'INFO': 50, 'WARN': 75, 'ERROR': 100}
        self.snippet_list = []
        self.template_seperator = '|'
        self.log('log_level: ' + self.log_level)

    def log(self, msg, level='INFO'):
        if self.log_level is 'NONE':
            return
        if self.log_level_list[self.log_level] > self.log_level_list[level]:
            return
        print('{0} - {1}: {2}'.format(self.util.plugin_name, level, msg))

    def run(self, paths=[]):
        # Find all Snippets
        self.load_include_folders()

        previewlist = []
        for snippet in self.snippet_list:
            previewlist.append([snippet.name, snippet.description])

        # Let the user select a snippet
        self.window.show_quick_panel(previewlist, functools.partial(self.run_snippet_vars, paths))

    def run_snippet_vars(self, paths, item):
        """
            After snippet selection, the user
            needs to fill all variables
        """
        # selection aborted
        if item is -1:
            return

        # no path selected
        if len(paths) is 0:
            return

        # only use one path
        path = paths[0]
        snippet = self.snippet_list[item]

        # load data now
        self.load_snippet_file(snippet)
        self.log('run snippet "{0}" on path "{1}"'.format(snippet.name, path))

        # Fill all variables
        self.util.multi_input(self.gen_input(snippet.vars), functools.partial(self.run_snippet_creation, snippet, path))

    def gen_input(self, var_dict):
        """
            To be used with multi_input.
            Sets all Values of the dictionary.

            ignores already set values
        """
        for i in var_dict:
            if type(var_dict[i]) is str:
                if i == var_dict[i]:
                    result = yield(i, var_dict[i])
                    var_dict[i] = result
            else:
                nr = yield(i, var_dict[i])
                if nr == -1:
                    var_dict[i] = ''
                else:
                    if type(var_dict[i][nr]) is dict:
                        var_dict[i] = var_dict[i][nr].get('value', '')
                    else:
                        var_dict[i] = var_dict[i][nr][0]

    def run_snippet_creation(self, snippet, path):
        snippet = self.replace_vars(snippet)
        exclude_file_extensions = self.settings.get('exclude_file_extensions', [])

        for item in snippet.files_and_folders:
            # normpath removes trailing slahes - no way
            # to tell the difference between file and folder!
            # soooo how to deal with os specific paths?
            # item = os.path.normpath(item)
            _templates = []
            if self.template_seperator in item:
                item, tmpl = item.split(self.template_seperator, 1)
                if self.template_seperator in tmpl:
                    _templates = tmpl.split(self.template_seperator)
                else:
                    _templates = [tmpl]

            _folder, _file = os.path.split(item)
            newfolder = self.util.resolve_path(_folder, path)
            if not os.path.isdir(newfolder):
                self.log('create folders: ' + newfolder)
                os.makedirs(newfolder)

            if _file:
                _file = self.util.resolve_path(item, path)
                if not os.path.isfile(_file):
                    self.log('create file: ' + _file)
                    self.util.touch_file(_file)
                    if _templates:
                        for _template in _templates:
                            if _template.startswith('<') and _template.endswith('>'):
                                # content
                                content_key = _template[1:-1]
                                self.log('fill file with content: ' + content_key)
                                content = snippet.content.get(content_key, '')
                            else:
                                # file:
                                _template = self.util.resolve_path(_template, snippet.dir)
                                self.log('fill file with file: ' + _template)
                                # plain copy binary files
                                ext = os.path.splitext(_template)[1][1:]
                                if ext in exclude_file_extensions:
                                    shutil.copyfile(_template, _file)
                                    continue
                                content = self.util.get_file_content(_template)
                            content = self.expand_variables(content, snippet.vars)
                            self.util.put_file_content(_file, content)
                    # After the files are created and filled with content, open them for the user
                    if self.settings.get('open_created_files', True):
                        ext = os.path.splitext(_file)[1][1:]
                        if ext not in exclude_file_extensions:
                            self.window.open_file(_file)

    def replace_vars(self, snippet):
        for i, item in enumerate(snippet.files_and_folders):
            item = self.expand_variables(item, snippet.vars)
            snippet.files_and_folders[i] = item
        return snippet

    def expand_variables(self, value, variables):
        """
            sublimes expand_variables will remove words
            beginning with an unescaped $, so we do it
            yourselfes.
        """
        for v in variables:
            pattern = '\$\{'+re.escape(v)+'\}'
            replace = variables.get(v, '')
            value = re.sub(pattern, replace, value)
        return value

    def find_vars(self, txt):
        """
            Find all sublime text style variables
            in the text, e.g. "${name}"
        """
        variables = re.findall('\$\{([^\}]*)\}', txt, re.MULTILINE)
        # Removes Doublettes
        variables = self.util.merge_lists(variables)
        # Make it a dictionary
        variables = dict(zip(variables, variables))
        return variables

    def special_vars(self):
        """
            Generates some usefull variables like
            Date, Time
        """
        today = datetime.datetime.today()
        variables = {
            "_timestamp": today.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "_datetime": today.strftime('%Y-%m-%d %H:%M'),
            "_date": today.strftime('%Y-%m-%d'),
            "_time": today.strftime('%H:%M')
        }
        return variables

    def template_files(self, file_list):
        """
            Finds the 1. the name of the file to be
            created and 2. the file(s) being used as
            template for it
        """
        result = {}
        for path in file_list:
            if self.template_seperator in path:
                # capture everything before and after the first "|"
                k, v = path.split(self.template_seperator, 1)
                result = self.util.merge_dicts(result, {k: v})
        return result

    def load_snippet_file(self, snippet):
        """
            The snippet json file needs to be
            loaded and somewhat parsed
        """
        # First thing is to check, wich files
        # are going to be used
        files_and_folders = '\n'.join(snippet.files_and_folders)

        # There may be variables used in the paths
        path_vars = self.find_vars(files_and_folders)

        # Files to be used for the template
        template_files = self.template_files(snippet.files_and_folders)

        # each template file may contain variables
        # so we need to find those too
        exclude_file_extensions = self.settings.get('exclude_file_extensions', [])
        template_file_vars = {}
        for i in template_files:
            # there may be more than one template:
            if self.template_seperator in template_files[i]:
                templates = template_files[i].split(self.template_seperator)
            else:
                templates = [template_files[i]]

            for template in templates:
                # paths in the snippet file are of course relative to the snippet file
                template_path = self.util.resolve_path(template, snippet.dir)

                # Do not search in those files (images, binary data etc.)
                ext = os.path.splitext(template)[1][1:]
                if ext in exclude_file_extensions:
                    continue

                if os.path.exists(template_path):
                    template_content = self.util.get_file_content(template_path)
                    new_vars = self.find_vars(template_content)
                    template_file_vars = self.util.merge_dicts(template_file_vars, new_vars)

        # extract variables from inline content
        for template_content in snippet.content.values():
            new_vars = self.find_vars(template_content)
            template_file_vars = self.util.merge_dicts(template_file_vars, new_vars)

        # Template variables set in the snippet file
        template_vars = snippet.vars

        # Global variables set in the settings file
        global_vars = self.settings.get('vars')

        # Sublime own variables such as "folder", "project", "project_name" etc.
        sublime_vars = self.window.extract_variables()

        # Generated variables
        special_vars = self.special_vars()

        # absolutely all variables to be used
        snippet.vars = self.util.merge_dicts(path_vars, template_file_vars, sublime_vars, global_vars, template_vars, special_vars)

    def load_snippet_preview(self, path):
        # the filepath sould be already absolute and existing
        snippet_content = self.util.get_file_content(path)

        try:
            snippet_data = json.loads(snippet_content)
        except:
            self.log('malformed json in "{0}"'.format(path), 'ERROR')
            return

        snippet = SnippetFile(
            snippet_data.get('name', 'UNNAMED'),
            snippet_data.get('description', ''),
            snippet_data.get('files_and_folders', []),
            snippet_data.get('content', {}),
            snippet_data.get('vars', {}),
            path
        )
        self.snippet_list.append(snippet)

    def load_include_folders(self):
        self.snippet_list = []
        include_folders = self.settings.get('include_folders')

        for folder in include_folders:
            # Rewrite the path to something more usefull
            folder = self.util.resolve_path(folder, self.util.get_plugin_dir())

            # Inform user about misconfiguration
            if not os.path.exists(folder):
                self.log('The folder "{0}" in "include_folders" does not exists'.format(folder), 'WARN')
                continue
            self.log('Scanning "{0}" from "include_folders"'.format(folder))

            # Look for .json files in valid folders
            for file in os.listdir(folder):
                if file.endswith(".json"):
                    self.load_snippet_preview(os.path.join(folder, file))
