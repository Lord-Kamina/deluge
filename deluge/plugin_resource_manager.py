#
# Copyright (C) 2024 Gregorio Litenstein <g.litenstein@gmail.com>
#
# This file is part of Deluge and is licensed under GNU General Public License 3.0, or later, with
# the additional special exception to link portions of this program with the OpenSSL library.
# See LICENSE for more details.
#

"""PluginResourceManager"""

import logging
import sys
from contextlib import ExitStack
from os.path import isfile
from pathlib import Path
from threading import Lock

if sys.version_info >= (3, 9):
    from importlib.resources import as_file, files
else:
    from importlib_resources import as_file, files

if sys.version_info >= (3, 10):
    from importlib.metadata import packages_distributions
else:
    from importlib_metadata import packages_distributions

log = logging.getLogger(__name__)


class PluginResourceManager:
    """PluginResourceManager handles access to plugin resources by looking over creation of copies on disk"""

    class FileContextManager:
        """FileContextManager helps us keep track of open files to avoid creating multiple copies of any given file."""

        def __init__(self):
            self.files_open: dict[str, Path] = {}
            self.stack = ExitStack()

        def reset(self):
            with PluginResourceManager.resource_manager_lock:
                self.stack.pop_all().close()
                self.files_open.clear()

    resource_manager_lock = Lock()
    # Just in case, share a lock to prevent race conditions.
    resource_managers: dict[str, FileContextManager] = {}
    # We keep a FileContextManager for each enabled plugin.

    @classmethod
    def resource_filename(cls, module: str, path: str) -> str:
        """Try to reuse previously accessed resources, and makes new copies if we can't"""
        try:
            file = as_file(files(module) / path)
            package_name = packages_distributions()[module][0]
            if module not in cls.resource_managers:
                with cls.resource_manager_lock:
                    cls.resource_managers.update(
                        {module: PluginResourceManager.FileContextManager()}
                    )
            fs_path = Path()
            if path not in cls.resource_managers[module].files_open:
                fs_path = cls.resource_managers[module].stack.enter_context(file)
            else:
                fs_path = cls.resource_managers[module].files_open[path]
                if not isfile(fs_path):
                    fs_path = cls.resource_managers[module].stack.enter_context(file)
        except ModuleNotFoundError as e:
            raise ValueError(
                f'Can\'t determine version for module {module} which maps to package: {package_name}'
            ) from e
        except FileNotFoundError as e:
            raise ValueError(f'File not found: {path}') from e
        with cls.resource_manager_lock:
            cls.resource_managers[module].files_open.update({path: fs_path})
        return str(fs_path)

    @classmethod
    def exists_for(cls, name: str) -> bool:
        return name in cls.resource_managers

    @classmethod
    def prepare_for(cls, name: str):
        cls.clear_for(name)
        with cls.resource_manager_lock:
            cls.resource_managers.update(
                {name: PluginResourceManager.FileContextManager()}
            )

    @classmethod
    def clear_for(cls, name: str):
        if name in cls.resource_managers:
            cls.resource_managers[name].reset()
            with cls.resource_manager_lock:
                del cls.resource_managers[name]
