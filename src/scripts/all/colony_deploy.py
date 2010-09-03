#!/usr/bin/python
# -*- coding: Cp1252 -*-

# Hive Colony Framework
# Copyright (C) 2008 Hive Solutions Lda.
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

__author__ = "Jo�o Magalh�es <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision: 9911 $"
""" The revision number of the module """

__date__ = "$LastChangedDate: 2010-08-30 11:04:12 +0100 (seg, 30 Ago 2010) $"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "GNU General Public License (GPL), Version 3"
""" The license for the module """

import os
import sys
import json
import types
import getopt

USAGE = "Help:\n\
--help[-h] - prints this message\n\
--verbose[-v] - starts the program in verbose mode\n\
--manager_dir[-m]=(PLUGIN_DIR) - sets the plugin directory to be used by the deployer\n"
""" The usage string for the command line arguments """

BRANDING_TEXT = "Hive Colony Deployer %s (Hive Solutions Lda. r1:Mar 19 2008)"
""" The branding text value """

VERSION = "1.0.0"
""" The version value """

VERSION_PRE_TEXT = "Python "
""" The version pre text value """

DEFAULT_PATH_VALUE = os.path.dirname(os.path.realpath(__file__))
""" The default path """

DEFAULT_MANAGER_PATH_VALUE = os.path.normpath(os.path.realpath(DEFAULT_PATH_VALUE + "/../.."))
""" The default manager path """

COLONY_HOME_ENVIRONMENT = "COLONY_HOME"
""" The colony home environment variable name """

SEPCIFICATION_FILE_NAME = "specification.json"
""" The specification file name """

REQUIRED_VALUES = ("platform", "id", "version")
""" The tuple of required values """

def print_information():
    """
    Prints the system information for the command line.
    """

    # print the branding information text
    print BRANDING_TEXT % VERSION

    # print the python information
    print VERSION_PRE_TEXT + sys.version

def usage():
    print USAGE

def update_system_path():
    """
    Updates the current system path, with the extra
    paths required for the normal functioning.
    """

    # adds the default path to the system path
    sys.path.insert(0, os.path.normpath(os.path.realpath(DEFAULT_PATH_VALUE + "/../lib")))

def log(message, verbose):
    if not verbose:
        return

    print message

def main():
    import colony_zip

    try:
        if len(sys.argv) < 2:
            raise Exception("Invalid number of arguments")

        if sys.argv[1][0] in ("-", "--"):
            a = sys.argv[1:]
        else:
            a = sys.argv[2:]

        options, _args = getopt.getopt(a, "hvm:", ["help", "verbose", "manager_dir="])
    except Exception, exception:
        # prints the exception description
        print str(exception)

        # prints usage information
        usage()

        # exits in error
        sys.exit(2)

    # retrieves the file system encoding
    file_system_encoding = sys.getfilesystemencoding()

    # starts the options values
    verbose = False
    manager_path = os.environ.get(COLONY_HOME_ENVIRONMENT, DEFAULT_MANAGER_PATH_VALUE).decode(file_system_encoding)

    # iterates over all the options
    for option, value in options:
        if option in ("-h", "--help"):
            usage()
            sys.exit()
        elif option in ("-v", "--verbose"):
            verbose = True
        elif option in ("-m", "--manager_dir"):
            manager_path = value.decode(file_system_encoding)

    # prints the console information
    print_information()

    # creates the target path
    target_path = os.path.normpath(manager_path + "/plugins")

    # creates the specification file path
    specification_file_path = target_path + "/" + SEPCIFICATION_FILE_NAME

    # retrieves the package path
    package_path = sys.argv[1]

    # prints a log message
    log("Deploying '%s' to '%s'" % (package_path, manager_path), True)

    # prints a log message
    log("Unpacking package file '%s' using zip decoder" % (package_path), verbose)

    # creates a new zip (manager)
    zip = colony_zip.Zip()

    # unzips the package to the target path
    zip.unzip(package_path, target_path)

    try:
        # prints a log message
        log("Opening specification file '%s'" % (specification_file_path), verbose)

        # opens the specification file
        specification_file = open(specification_file_path)

        try:
            # reads the specification file, retrieving the contents
            specification_file_contents = specification_file.read()
        finally:
            # closes the specification file
            specification_file.close()

        # loads the json specification file contents
        specification = json.loads(specification_file_contents)

        # prints the specification
        #print_specification(specification)

        # retrieves the main file
        main_file = specification["main_file"]

        # splits the main file name into name and extension
        main_file_name, _mail_file_extension = os.path.splitext(main_file)

        # creates the new specification file name
        new_specification_file_name = main_file_name + ".json"

        # creates the new specification file path
        new_specification_file_path = target_path + "/" + new_specification_file_name

        # renames the specification file
        os.rename(specification_file_path, new_specification_file_path)

        # prints a log message
        log("Renaming specification file '%s' to '%s'" % (SEPCIFICATION_FILE_NAME, new_specification_file_name), verbose)
    except Exception, exception:
        # prints a log message
        log("Exception while renaming specification file '%s'" % unicode(exception), verbose)

        # removes the specification file
        os.remove(target_path + "/specification.json")

    log("Finished deployment", True)

def validate_specification(specification):
    # iterates over all the required values in the required values list
    for required_value in REQUIRED_VALUES:
        # in case the required value is not in the specification
        if not required_value in specification:
            # raises an exception
            raise Exception("Required value '%s' missing in specification file" % (required_value))

def print_specification(specification):
    # retrieves the required (mandatory) values
    platform = specification["platform"]
    id = specification["id"]
    version = specification["version"]

    # retrieves the optional values
    sub_platforms = specification.get("sub_platforms", [])
    name = specification.get("name", "")
    short_name = specification.get("short_name", "")
    description = specification.get("description", "")
    author = specification.get("author", "")
    capabilities = specification.get("capabilities", [])
    capabilities_allowed = specification.get("capabilities_allowed", [])
    dependencies = specification.get("dependencies", [])
    main_file = specification.get("main_file", [])
    resources = specification.get("resources", [])

    printa("Platform", platform)
    printa("Sub-Platforms", sub_platforms)
    printa("Id", id)
    printa("Name", name)
    printa("Short Name", short_name)
    printa("Description", description)
    printa("Version", version)
    printa("Author", author)
    printa("Capabilities", capabilities)
    printa("Capabilities Allowed", capabilities_allowed)
    printa("Dependencies", dependencies)
    printa("Main File", main_file)
    printa("Resources", resources)

def printa(key, value):
    # retrieves the type of the value
    value_type = type(value)

    # in case the value is a string
    if value_type in types.StringTypes:
        print key + ": " + value
    # in case the value is a list (of strings)
    elif value_type == types.ListType:
        print key,

        print ":" + str(value)

if __name__ == "__main__":
    update_system_path()
    main()
