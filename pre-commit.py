#!/usr/bin/env python

"""
Pender's pre-commit hook.

For more information, see:
    https://github.com/alexjurkiewicz/pender
"""

import os
import sys
import shutil
import subprocess
import tempfile
import logging

# CONFIG
PENDER_NAME = 'pre-commit'
PLUGINS_DIR = 'pre-commit-plugins/'
LOGLEVEL = logging.WARNING
# END CONFIG

TERM_BOLD = '\033[1m'
TERM_END = '\033[0m'


def initialise_logging():
    """Initialise logging."""
    logging.basicConfig(level=LOGLEVEL)


def install_check():
    """Ask if Pender should be installed."""
    source_path = sys.argv[0]
    repo_dir = os.path.dirname(source_path)
    install_q = "Install this pre-commit hook to {repo_dir}" \
                "/.git/hooks/pre-commit [Y/n]? "
    choice = raw_input(install_q.format(repo_dir=repo_dir))
    if choice in ('', 'Y', 'y', 'YES', 'yes', 'Yes'):
        dest_path = os.path.join(repo_dir, ".git/hooks/pre-commit")
        try:
            print 'cp -p {source} {dest}'.format(source=source_path,
                                                 dest=dest_path)
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


def autoupdate_check():
    """See if the repo version of Pender is newer, and fail if so."""
    git_dir = os.path.join(os.environ['GIT_DIR'])
    pender_repo_path = os.path.join(git_dir, '..', PENDER_NAME)
    pender_hook_path = os.path.join(git_dir, 'hooks', 'pre-commit')
    logging.debug("Comparing %s to %s", pender_repo_path, pender_hook_path)
    if os.stat(pender_repo_path).st_mtime > os.stat(pender_hook_path).st_mtime:
        print "Error: {name} has been updated, please run the repository's " \
              "copy to update your installed version.".format(name=PENDER_NAME)
        sys.exit(1)


def get_changed_files():
    """Return a list of changed files."""
    changed_files_cmd = ['git', 'diff-index', '--diff-filter=AM',
                         '--name-only', '--cached', 'HEAD']
    try:
        changed_files = subprocess.check_output(changed_files_cmd).splitlines()
    except subprocess.CalledProcessError as err:
        print "Couldn't determine changed files! Git error was:"
        print "$ {}".format(' '.join(changed_files_cmd))
        print err.output
        sys.exit(1)
    logging.debug("Found %s changed files: %s", len(changed_files),
                  ", ".join(changed_files))
    return changed_files


def create_temp_file(temp_tree, index_file):
    """
    Copy staged changes of index_file to same location in temp_tree.

    FIXME: This reads the entire file into memory.
    """
    repo_path = os.path.dirname(index_file).lstrip('/')
    temp_dirpath = os.path.join(temp_tree, repo_path)
    if repo_path and not os.path.isdir(temp_dirpath):
        os.makedirs(temp_dirpath, mode=0700)
    try:
        args = ['git', 'cat-file', 'blob', ':0:{}'.format(index_file)]
        cached_string = subprocess.check_output(args)
    except subprocess.CalledProcessError as err:
        print "Couldn't determine changed content for {}".format(index_file)
        print err.output
        sys.exit(1)
    temp_file = os.path.join(temp_dirpath, os.path.basename(index_file))
    with open(temp_file, 'w') as fil:
        fil.write(cached_string)
        del cached_string
    return temp_file


def get_plugins():
    """Return a list of available plugins."""
    plugins = []
    for p in os.listdir(PLUGINS_DIR):
        plugin = os.path.join(PLUGINS_DIR, p)
        if not os.path.isfile(plugin):
            logging.info("Non-file in plugin directory: %s", plugin)
            continue
        if not os.access([plugin], os.X_OK):
            logging.info("Non-executable file in plugin directory: %s", plugin)
            continue
        plugins.append(plugin)
    return plugins


def get_mime_type(f):
    """Return mime type of f (application/octet-stream if unknown)."""
    try:
        file_args = ['file', '--brief', '--mime-type', f]
        mime_type = subprocess.check_output(file_args).strip()
    except (subprocess.CalledProcessError, EnvironmentError) as err:
        logging.info("Couldn't determine MIME type of %s (\"%s\").", f, err)
        mime_type = 'application/octet-stream'
    return mime_type


def run_plugin(plugin, real_file, temp_file, mime_type):
    """Run plugin and return output only if vetoes the commit."""
    args = [plugin, real_file, temp_file, mime_type]
    try:
        p_output = subprocess.check_output(args, stderr=subprocess.STDOUT)
    except EnvironmentError as err:
        print "Unexpected error calling " \
            "{} (\"{}\"), skipping.".format(plugin, err)
    except subprocess.CalledProcessError as err:
        p_output = err.output
        if err.returncode == 10:
            return p_output
        else:
            print "Unexpected error calling " \
                "{} (\"{}\"), skipping.".format(plugin, err)
            return None


def process_changed_files(temp_tree, changed_files, plugins):
    """Process each changed file."""
    errors = 0
    for index_file in changed_files:
        temp_file = create_temp_file(temp_tree, index_file)

        # Determine MIME type
        mime_type = get_mime_type(index_file)

        # Call every plugin with this file
        for plugin in plugins:
            output = run_plugin(plugin, index_file, temp_file, mime_type)
            if output:
                errors += 1
                print "{bold}{file}:{end}".format(file=index_file,
                                                  bold=TERM_BOLD,
                                                  end=TERM_END)
                for line in output.splitlines():
                    print '    {line}'.format(line=line)

    if errors:
        print "{bold}Found {errors} errors, aborting commit.{end}".format(
            errors=errors, bold=TERM_BOLD, end=TERM_END)
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    initialise_logging()
    if 'GIT_DIR' not in os.environ:
        install_check()
    else:
        autoupdate_check()

    TEMP_TREE = tempfile.mkdtemp()
    try:
        process_changed_files(TEMP_TREE, get_changed_files(), get_plugins())
    except KeyboardInterrupt:
        sys.stdout.flush()
        sys.exit(1)
    finally:
        shutil.rmtree(TEMP_TREE)
    sys.exit(0)
