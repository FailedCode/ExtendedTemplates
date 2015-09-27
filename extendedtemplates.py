import sublime
import sublime_plugin
import os
import json
import re
import functools
import datetime


class SnippetFile(object):
    """
        Save all data from json file for later
    """

    def __init__(self, name, description, files_and_folders, var, path):
        self.name = name
        self.description = description
        self.files_and_folders = files_and_folders
        self.vars = var
        self.path = path


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
        f = open(path, "r")
        content = f.read()
        f.close()
        return content

    def put_file_content(self, path, content):
        f = open(path, "a")
        f.write(content)
        f.close()

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
                progress.caption, progress.initial_text = gen_function.send(result)
                sublime.active_window().show_input_panel(
                    progress.caption,
                    progress.initial_text,
                    progress, None, None
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
        self.log_level_list = {'NONE': 0, 'INFO': 50, 'ERROR': 100}
        self.snippet_list = []
        self.log('log_level: ' + self.log_level)

    def log(self, msg, level='INFO'):
        if self.log_level is 'NONE':
            return
        if self.log_level_list[self.log_level] < self.log_level_list[level]:
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
            if i == var_dict[i]:
                result = yield('set variable '+i, var_dict[i])
                var_dict[i] = result

    def run_snippet_creation(self, snippet, path):
        snippet = self.replace_vars(snippet)
        for item in snippet.files_and_folders:
            # normpath removes trailing slahes - no way
            # to tell the difference between file and folder!
            # soooo how to deal with os specific paths?
            # item = os.path.normpath(item)

            _template = ''
            if '|' in item:
                item, tmpl = re.findall('([^|]*)\|(.*)', item)[0]
                _template = self.util.resolve_path(tmpl, snippet.path)

            _folder, _file = os.path.split(item)
            newfolder = self.util.resolve_path(_folder, path)
            if not os.path.isdir(newfolder):
                self.log('create folders: ' + newfolder)
                os.makedirs(newfolder)

            if _file:
                _file = self.util.resolve_path(item, path)
                if not os.path.isfile(item):
                    self.log('create file: ' + _file)
                    self.util.touch_file(_file)
                    if _template:
                        self.log('fill file with: ' + _template)
                        content = self.util.get_file_content(_template)
                        content = sublime.expand_variables(content, snippet.vars)
                        self.util.put_file_content(_file, content)

    def replace_vars(self, snippet):
        for i, item in enumerate(snippet.files_and_folders):
            item = sublime.expand_variables(item, snippet.vars)
            snippet.files_and_folders[i] = item
        return snippet

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
            created and 2. the file being used as
            template for it
        """
        result = {}
        for path in file_list:
            if '|' in path:
                # capture everything before and after "|"
                templates = re.findall('([^|]*)\|(.*)', path)
                result = self.util.merge_dicts(result, templates)
        return result

    def load_snippet_file(self, path):
        """
            The snippet json files need to be
            loaded and somewhat parsed so they can
            be chosen and used
        """

        # the filepath sould be already absolute and existing
        text = self.util.get_file_content(path)

        # todo: try/catch malformed json
        snippet_data = json.loads(text)

        # First thing is to check, wich files
        # are going to be used
        files_and_folders = '\n'.join(snippet_data['files_and_folders'])

        # There may be variables used in the paths
        path_vars = self.find_vars(files_and_folders)

        # Files to be used for the template
        template_files = self.template_files(snippet_data['files_and_folders'])

        # each template file may contain variables
        # so we need to find those too
        template_file_vars = []
        for i in template_files:
            # paths in the snippet file are of course relative to the snippet file
            template_path = self.util.resolve_path(template_files[i], os.path.dirname(path))
            if os.path.exists(template_path):
                text = self.util.get_file_content(template_path)
                new_vars = self.find_vars(text)
                template_file_vars = self.util.merge_dicts(template_file_vars, new_vars)

        # Template variables set in the snippet file
        template_vars = snippet_data['vars']

        # Global variables set in the settings file
        global_vars = self.settings.get('vars')

        # Generated variables
        special_vars = self.special_vars()

        # absolutely all variables to be used
        all_vars = self.util.merge_dicts(path_vars, template_file_vars, template_vars, global_vars, special_vars)

        snippet = SnippetFile(
            snippet_data['name'],
            snippet_data['description'],
            snippet_data['files_and_folders'],
            all_vars,
            os.path.dirname(path)
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
                self.log('The folder "{0}" in "include_folders" does not exists'.format(folder), 'ERROR')
                continue

            # Look for .json files in valid folders
            for file in os.listdir(folder):
                if file.endswith(".json"):
                    self.load_snippet_file(os.path.join(folder, file))
