#!/usr/bin/env python

'''
Pender's pre-commit hook. Please see README.md for more information.
'''

# CONFIG
PLUGINS_DIR = 'pender-plugins/'
# END CONFIG

import os
import sys
import shutil
import subprocess
import tempfile

TERM_BOLD = '\033[1m'
TERM_END = '\033[0m'


def autoupdate_check():
    '''
    autoupdate check
    '''
    if 'GIT_DIR' not in os.environ:
        source_path = sys.argv[0]
        repo_dir = os.path.dirname(source_path)
        install_q = "Install this pre-commit hook to {repo_dir}/.git/hooks/pre-commit [Y/n]? "
        choice = raw_input(install_q.format(repo_dir=repo_dir))
        if choice in ('', 'Y', 'y', 'YES', 'yes', 'Yes'):
            dest_path = os.path.join(repo_dir, ".git/hooks/pre-commit")
            try:
                shutil.copyfile(source_path, dest_path)
                shutil.copystat(source_path, dest_path)
                print "Done."
                _rc = 0
            except StandardError as err:
                print "Failed! ({e})".format(e=err)
                _rc = 1
        else:
            _rc = 1
        sys.exit(_rc)


def get_changed_files():
    '''
    Return a list of changed files
    '''
    changed_files_cmd = ['git', 'diff-index', '--diff-filter=AM', '--name-only', '--cached', 'HEAD']
    try:
        changed_files = subprocess.check_output(changed_files_cmd).splitlines()
    except subprocess.CalledProcessError as err:
        print "Couldn't determine changed files! Git error was:"
        print "$ {}".format(' '.join(changed_files_cmd))
        print err.output
        sys.exit(1)
    return changed_files


def create_temp_file(temp_tree, index_file):
    '''
    Create temp file
    '''
    repo_path = os.path.dirname(index_file).lstrip('/')
    temp_dirpath = os.path.join(temp_tree, repo_path)
    if repo_path and not os.path.isdir(temp_dirpath):
        os.makedirs(temp_dirpath, mode=0700)
    try:
        git_cat_file_command = ['git', 'cat-file', 'blob', ':0:{}'.format(index_file)]
        cached_string = subprocess.check_output(git_cat_file_command)
    except subprocess.CalledProcessError as err:
        print "Couldn't determine changed content for {}".format(index_file)
        print err.output
        sys.exit(1)
    temp_file = os.path.join(temp_dirpath, os.path.basename(index_file))
    with open(temp_file, 'w') as fil:
        fil.write(cached_string)
        del cached_string  # TODO: should really pipe without storing in a temp variable for performance reasons

    return temp_file


def process_changed_files(temp_tree):
    '''
    process each changed file
    '''
    errors = 0
    plugins = [os.path.join(PLUGINS_DIR, plugin) for plugin in os.walk(PLUGINS_DIR).next()[2]]
    changed_files = get_changed_files()
    for index_file in changed_files:
        temp_file = create_temp_file(temp_tree, index_file)

        # Determine MIME type
        try:
            mime_type = subprocess.check_output(['file', '--brief', '--mime-type', index_file]).strip()
        except subprocess.CalledProcessError:
            mime_type = 'application/octet-stream'

        # Call every plugin with this file
        for plugin in plugins:
            try:
                plugin_command = [plugin, index_file, temp_file, mime_type]
                plugin_output = subprocess.check_output(plugin_command, stderr=subprocess.STDOUT)
            except OSError as err:
                # XXX: should be determined when building plugins
                if err.errno == 13:
                    print "Skipping non-executable file in plugins directory '{plugin}'".format(plugin=plugin)
                    continue
            except subprocess.CalledProcessError as err:
                plugin_output = err.output
                if err.returncode == 10:
                    errors += 1
                    print "{bold}{file}:{end}".format(
                          file=index_file, plugin=os.path.basename(plugin), bold=TERM_BOLD, end=TERM_END)
            if plugin_output:
                for line in plugin_output.splitlines():
                    print '    {line}'.format(line=line)
    if errors:
        print "{bold}Found {errors} errors, aborting commit.{end}".format(errors=errors, bold=TERM_BOLD, end=TERM_END)
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    autoupdate_check()

    TEMP_TREE = tempfile.mkdtemp()
    try:
        process_changed_files(TEMP_TREE)
    except KeyboardInterrupt:
        sys.stdout.flush()
        sys.exit(1)
    finally:
        shutil.rmtree(TEMP_TREE)
