#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Colony Framework
# Copyright (c) 2008-2012 Hive Solutions Lda.
#
# This file is part of Hive Colony Framework.
#
# Hive Colony Framework is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hive Colony Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hive Colony Framework. If not, see <http://www.gnu.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2012 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "GNU General Public License (GPL), Version 3"
""" The license for the module """

import os
import sys
import glob
import atexit
import warnings
import traceback

CONFIG_FILE_ENV = "COLONY_CONFIG_FILE"
""" The name of the environment variable to be used
to retrieve the path to the configuration file """

DEFAULT_CONFIG_PATH = "config/python/development.py"
""" The path to the default configuration file to be
used in case no path is specified using the environment
variable bases strategy """

# retrieves the base path for the current file and uses
# it to insert it in the current system path in case it's
# not already present (required for module importing)
base_path = os.path.dirname(__file__)
if not base_path in sys.path: sys.path.insert(0, base_path)

import colony.base.system

# registers the ignore flag in the deprecation warnings so that
# no message with this kind of warning is printed (clean console)
warnings.filterwarnings("ignore", category = DeprecationWarning)

# tries to retrieve the run mode from the currently set
# environment variables, in case of failure defaults to
# the default value
run_mode = os.environ.get("run_mode", "development")

# tries to retrieve the configuration file from the environment
# variable associated in case it fails uses the default configuration
# file path then joins the "relative" file path to the base path
# and resolves it as an absolute path
config_file_path = os.environ.get(CONFIG_FILE_ENV, None) or DEFAULT_CONFIG_PATH
config_file_path = os.path.join(base_path, config_file_path)
config_file_path = os.path.abspath(config_file_path)

# retrieves the name of the directory containing the configuration
# files and adds it to the system path, so that it's possible to
# import the configuration file module
configuration_directory_path = os.path.dirname(config_file_path)
sys.path.insert(0, configuration_directory_path)

# retrieves the configuration file base path from the configuration
# file path, this values is going to be used to retrieve the "final"
# module name to be imported in the python interpreter
config_file_base_path = os.path.basename(config_file_path)

# retrieves the configuration module name and the configuration
# module extension by splitting the configuration base path into
# base name and extension and then imports the referring module
configuration_module_name, _configuration_module_extension = os.path.splitext(config_file_base_path)
colony_configuration = __import__(configuration_module_name)

# initializes the lists that will contain both the path to the
# plugins and the paths to the configuration (meta) files
plugin_paths = []
meta_paths = []

# iterates over each of the plugin paths to resolve them using
# the glob based approach then "takes" the final list into a
# final step of absolute path normalization
for plugin_path in colony_configuration.plugin_path_list:
    plugin_paths += glob.glob(os.path.join(base_path, plugin_path))
plugin_paths = [os.path.abspath(plugin_path) for plugin_path in plugin_paths]

# iterates over each of the meta paths to resolve them using
# the glob based approach then "takes" the final list into a
# final step of absolute path normalization
for meta_path in colony_configuration.meta_path_list:
    meta_paths += glob.glob(os.path.join(base_path, meta_path))
meta_paths = [os.path.abspath(meta_path) for meta_path in meta_paths]

# creates the plugin manager instance with the current file path
# as the manager path and the corresponding relative log path,
# then provides the plugin and meta paths and unsets the global
# loop strategy (avoids blocking the process), note also that
# threads are disallowed to avoid creation of extra threads, the
# signal handlers are disabled to avoid collisions
plugin_manager = colony.base.system.PluginManager(
    manager_path = base_path,
    logger_path = os.path.join(base_path, "log"),
    plugin_paths = plugin_paths,
    meta_paths = meta_paths,
    loop = False,
    threads = False,
    signals = False,
    run_mode = run_mode
)
return_code = plugin_manager.load_system()

def application(environ, start_response):
    try:
        # retrieves the wsgi plugin and uses it to handle
        # the wsgi request (request redirection) any inner
        # exception should be handled and an error http
        # message should be returned to the end user
        wsgi_plugin = plugin_manager.get_plugin("pt.hive.colony.plugins.wsgi")
        sequence = wsgi_plugin.handle(environ, start_response)
    except:
        # in case the run mode is development the exception should
        # be processed and a description sent to the output
        if run_mode == "development":
            # prints a description of the exception and then
            # sends the traceback of it to the output
            traceback.print_exc(file = sys.stdout)

        # raises the exception back to the stack to be handled
        # by the upper levels
        raise

    # returns the sequence object that may be used by the caller
    # method to retrieve the contents of the message to be sent
    return sequence

@atexit.register
def unload_system():
    # unloads the plugin manager system releasing all
    # the used resources and killing all the threads
    # this should be enough to return the control to
    # the embedding process
    plugin_manager.unload_system()

if __name__ == "__main__":
    import wsgiref.simple_server
    httpd = wsgiref.simple_server.make_server("0.0.0.0", 8080, application)
    print >> sys.stderr, "Running on http://0.0.0.0:8080/"
    httpd.serve_forever()
