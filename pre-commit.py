#!/usr/bin/env python
"""
Pender pre-commit hook.

For more information see https://github.com/alexjurkiewicz/pender
"""

import os
import sys
import shutil
import subprocess
import tempfile
import logging

PENDER_NAME = 'pre-commit.py'
PLUGINS_DIR = 'pre-commit-plugins/'

TERM_BOLD = '\033[1m'
TERM_END = '\033[0m'
TERM_RED = '\033[31m'
TERM_YELLOW = '\033[33m'
PENDER_EXIT_OK = 0
PENDER_EXIT_ERR = 1
PENDER_EXIT_VETO = 10


class PenderError(Exception):
    """Simple wrapper."""

    pass


class PenderLoggingFormatter(logging.Formatter):
    """Custom log formatter.

    Colourise error/warning messages. Based off:
    http://stackoverflow.com/questions/1343227/can-pythons-logging-format-be-modified-depending-on-the-message-log-level
    """

    def __init__(self):
        """Set up simple override for err/warn messages."""
        self.base_fmt = "{pender}: %(message)s".format(pender=PENDER_NAME)
        self.err_fmt = "%s%s%s" % (TERM_RED, self.base_fmt, TERM_END)
        self.warn_fmt = "%s%s%s" % (TERM_YELLOW, self.base_fmt, TERM_END)
        logging.Formatter.__init__(self, self.base_fmt)

    def format(self, record):
        """Set the format string based on severity.

        This will also cause issues for logging errors generated by libs we
        use, but since we don't use libs skip the extra code to avoid this.
        """
        if record.levelno == logging.ERROR:
            self._fmt = self.err_fmt
        elif record.levelno == logging.WARN:
            self._fmt = self.warn_fmt
        else:
            self._fmt = self.base_fmt

        # Call the original formatter class to do the grunt work
        return logging.Formatter.format(self, record)


def initialise_logging():
    """Initialise logging."""
    if 'PENDER_DEBUG' in os.environ:
        level = logging.DEBUG
    else:
        level = logging.INFO

    fmt = PenderLoggingFormatter()
    hdlr = logging.StreamHandler(sys.stdout)
    hdlr.setFormatter(fmt)
    logging.root.addHandler(hdlr)
    logging.root.setLevel(level)


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
            shutil.copyfile(source_path, dest_path)
            shutil.copystat(source_path, dest_path)
        except StandardError as err:
            print "Failed! ({e})".format(e=err)
            return PENDER_EXIT_ERR
    else:
        return PENDER_EXIT_ERR
    install_plugins()
    return PENDER_EXIT_OK


def autoupdate_check():
    """See if the repo version of Pender is newer, and fail if so."""
    git_dir = os.path.join(os.environ['GIT_DIR'])
    pender_repo_path = os.path.join(git_dir, '..', PENDER_NAME)
    pender_hook_path = os.path.join(git_dir, 'hooks', 'pre-commit')
    logging.debug("Comparing %s to %s", pender_repo_path, pender_hook_path)
    if os.stat(pender_repo_path).st_mtime > os.stat(pender_hook_path).st_mtime:
        logging.error("%s has been updated, please run the repository's "
                      "copy to update your installed version.", PENDER_NAME)
        sys.exit(1)


def install_plugins():
    """Run plugin install checks."""
    for plugin in plugins():
        plugin_install(plugin)


def changed_files():
    """Iterable of changed files."""
    changed_files_cmd = ['git', 'diff-index', '--diff-filter=AM',
                         '--name-only', '--cached', 'HEAD']
    try:
        files = subprocess.check_output(changed_files_cmd).splitlines()
    except subprocess.CalledProcessError as err:
        raise PenderError(
            "Couldn't determine changed files! Git error was:\n$ %s\n%s",
            ' '.join(changed_files_cmd), err.output)
    logging.debug("Found %s changed files: %s", len(files), ", ".join(files))
    return files


def create_temp_file(temp_tree, index_file):
    """Copy staged changes of index_file to same location in temp_tree."""
    git_args = ['git', 'cat-file', 'blob', ':0:{}'.format(index_file)]
    repo_path = os.path.dirname(index_file).lstrip('/')
    temp_dirpath = os.path.join(temp_tree, repo_path)

    if repo_path and not os.path.isdir(temp_dirpath):
        os.makedirs(temp_dirpath, mode=0700)

    # We can't use check_output here, since we want to capture stderr
    # for error diagnostics but check_output can only do so by merging into
    # stdout (which we're using).
    temp_file = os.path.join(temp_dirpath, os.path.basename(index_file))
    with open(temp_file, 'w') as dest:
        try:
            git = subprocess.Popen(git_args,
                                   stdout=dest,
                                   stderr=subprocess.PIPE)
        except OSError as e:
            raise PenderError(e)
        _, stderr = git.communicate()
        if git.returncode:
            raise PenderError(stderr)
    return temp_file


def plugins():
    """Iterable of available plugins."""
    for path in os.listdir(PLUGINS_DIR):
        plugin = os.path.join(PLUGINS_DIR, path)
        if not os.path.isfile(plugin):
            logging.info("Non-file in plugin directory: %s", plugin)
            continue
        if not os.access(plugin, os.X_OK):
            logging.info("Non-executable file in plugin directory: %s", plugin)
            continue
        yield plugin


def get_mime_type(path):
    """Return mime type of f (application/octet-stream if unknown)."""
    try:
        file_args = ['file', '--brief', '--mime-type', path]
        mime_type = subprocess.check_output(file_args).strip()
    except (subprocess.CalledProcessError, EnvironmentError) as err:
        logging.info("Couldn't determine MIME type of %s (\"%s\").", path, err)
        mime_type = 'application/octet-stream'
    return mime_type


def plugin_install(path):
    """Run plugin install and log any output."""
    args = (path, 'install')
    try:
        output = subprocess.check_output(args, stderr=subprocess.STDOUT)
        for line in output.splitlines():
            logging.info("%s: %s", path, line)
    except subprocess.CalledProcessError as e:
        logging.error("%s failed during setup. Output:\n%s", path, e.output)


def plugin_check(path, real_file, temp_file, mime_type):
    """Run plugin and return (veto, output)."""
    args = (path, 'check', real_file, temp_file, mime_type)
    try:
        plugin = subprocess.Popen(args,
                                  stderr=subprocess.STDOUT,
                                  stdout=subprocess.PIPE)
    except OSError as err:
        logging.warning("Couldn't run %s (%s), skipping.", plugin, err)
        return (False, '')
    output, _ = plugin.communicate()
    if plugin.returncode == PENDER_EXIT_OK:
        return (False, output)
    elif plugin.returncode == PENDER_EXIT_VETO:
        return (True, output)
    else:
        logging.warning("%s returned unexpected exit code %s, skipping.",
                        plugin, plugin.returncode)
        return (False, output)


def process_changed_files(temp_tree):
    """Process each changed file."""
    errors = 0
    for index_file in changed_files():
        plugin_errors = 0
        try:
            temp_file = create_temp_file(temp_tree, index_file)
        except PenderError as e:
            logging.error("Couldn't create temp file for %s (%s)", index_file,
                          e)
            errors += 1
            continue
        mime_type = get_mime_type(index_file)
        for plugin in plugins():
            veto, output = plugin_check(plugin, index_file, temp_file,
                                        mime_type)
            if veto:
                plugin_errors += 1
                logging.info("%s%s vetoes %s:%s", TERM_RED + TERM_BOLD,
                             os.path.basename(plugin), index_file, TERM_END)
            for line in output.splitlines():
                logging.info('%s: %s', os.path.basename(plugin), line)
        if plugin_errors:
            errors += 1

    if errors:
        logging.info("%sFound errors in %s files, aborting commit.%s",
                     TERM_BOLD, errors, TERM_END)
        return 1
    else:
        return 0


if __name__ == '__main__':
    initialise_logging()
    if 'GIT_DIR' not in os.environ:
        rc = install_check()
    else:
        autoupdate_check()
        try:
            TEMP_TREE = tempfile.mkdtemp()
            rc = process_changed_files(TEMP_TREE)
        except KeyboardInterrupt:
            sys.stdout.flush()
            rc = 1
        except PenderError as e:
            logging.error(e)
            rc = 1
        finally:
            shutil.rmtree(TEMP_TREE)
    sys.exit(rc)
