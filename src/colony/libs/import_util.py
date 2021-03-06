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

import sys

GLOBALS_REFERENCE_VALUE = "_globals"
""" The globals reference value """

LOCALS_REFERENCE_VALUE = "_locals"
""" The locals reference value """

def __import__(module_name, persist_value = True):
    """
    Importer function to be used in the process of importing
    a module referred in inverted way.
    The optional persist value may be used to control if the
    globals/locals reference value must be set in the caller module
    in case it has been retrieved from a parent caller (cache).
    This function should be used in cases where the inversion injection
    was made using the data helper.

    @type module_name: String
    @param module_name: The name of the module to be imported.
    @type persist_value: bool
    @param persist_value: If the globals/locals value shall be
    persisted in the caller in case it's is not available there.
    @rtype: Module
    @return: The imported module.
    """

    # unsets the module reference
    module = None

    # starts the index counter value
    # to start in the previous caller
    index = 1

    try:
        # iterates continuously
        while True:
            # retrieves the caller of the importer method
            caller = sys._getframe(index)

            # in case the module name exists in the globals map
            # of the caller
            if module_name in caller.f_globals.get(GLOBALS_REFERENCE_VALUE, {}):
                # retrieves the module from the globals map of the caller
                module = caller.f_globals[GLOBALS_REFERENCE_VALUE][module_name]

                # breaks the loop
                break
            # in case the module name exists in the locals map
            # of the caller
            elif module_name in caller.f_globals.get(LOCALS_REFERENCE_VALUE, {}):
                # retrieves the module from the locals map of the caller
                module = caller.f_globals[LOCALS_REFERENCE_VALUE][module_name]

                # breaks the loop
                break

            # increments the index counter
            index += 1
    except ValueError:
        # raises a runtime error because it could
        # not retrieve the module
        raise ImportError("No module named '%s' found in global or local references" % module_name)

    # raise a runtime error in case the module
    # is not found (problem in the import)
    if not module: raise ImportError("No module named '%s' found in global or local references" % module_name)

    # in case the module value was retrieved from an upper
    # calling layer and the persist value flag is set (cache)
    # the module value must be persisted in the direct caller
    if index > 1 and persist_value:
        # retrieves the (direct) caller of the importer method
        # and sets the module in the globals reference value
        caller = sys._getframe(1)
        globals_reference = caller.f_globals.get(GLOBALS_REFERENCE_VALUE, {})
        globals_reference[module_name] = module
        caller.f_globals[GLOBALS_REFERENCE_VALUE] = globals_reference

    # returns the module
    return module

def reload_import(path, hard = True):
    """
    Reloads the import (module) referred in the system modules
    by the given path.
    This reload is triggered synchronously and so at the return
    of this function the module should be reloaded.

    There are two modes of operation for reloading:
    The "hard" operation mode removes the module from the system
    modules and updates the environment.
    The "soft" operation modes "just" reloads the module in the
    current environment.

    @type path: String
    @param path: The (package) path to the module to be reloaded.
    This path should be the same as the one referring the module
    in the system modules.
    @type hard: bool
    @param hard: If an "hard" reload approach musb be taken to provide
    the reload process. The hard reload approach removes the path
    from the system modules map.
    """

    # in case the path is not present in the
    # system modules no need to reload
    if not path in sys.modules:
        # returns immediately
        return

    # in case the hard approach for reloading is
    # taken the system modules should be changed
    if hard:
        # retrieves the module for the given path from
        # system module and then removes it from the system
        # modules and then deletes it from the virtual
        # machine environment
        module = sys.modules[path]
        del sys.modules[path]
        del module
    # otherwise the "soft" reload provides the normal
    # module reload method
    else:
        # retrieves the module for the given path from
        # system module and then forces a reload on the
        # module (to flush the contents)
        module = sys.modules[path]
        reload(module)
