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

MESSAGE_VALUE = "message"
""" The message operation value """

ACTION_VALUE = "action"
""" The action operation value """

PROGRESS_VALUE = "progress"
""" The progress operation value """

GLOBAL_HANDLERS_MAP = {}
""" The global handlers map to be used by default if
no specific handlers map is defined """

def notify(operation_name, handlers_map = None, *arguments, **named_arguments):
    """
    Notifies an handler defined in the given handlers map about
    the provided operation.
    The provided arguments are sent to the operation handler
    as parameters.

    @type operation_name: String
    @param operation_name: The name of the operation to call
    the handler.
    @type handlers_map: Dictionary
    @param handlers_map: The map containing the operation
    handlers.
    @rtype: bool
    @return: The result of the notification, useful for some
    types of operations.
    """

    # retrieves the appropriate handlers map, defaulting
    # to the global handlers map in case none is provided
    handlers_map = handlers_map or GLOBAL_HANDLERS_MAP

    # retrieves the operation method from the handlers
    # map (if possible)
    operation_method = handlers_map.get(operation_name, None)

    # in case the operation method was not found
    # (not possible to execute the handler), returns
    # immediately (as valid)
    if not operation_method: return True

    # checks if the operation method type is "iterable" and
    # in case it's not encapsulates the operation method
    # around a tuple value to make it "iterable"
    if not hasattr(operation_method, "__iter__"): operation_method = (operation_method,)

    # iterates over all the operation method contained in the
    # operation method sequence, to run their actions
    for _operation_method in operation_method:
        # calls the operation method with the arguments and
        # and "saves" the return value of it
        return_value = _operation_method(*arguments, **named_arguments)

    # returns the last return value representing the
    # final result for the notification
    return return_value

def message(handlers_map = None, *arguments, **named_arguments):
    """
    Shortcut method to call the handlers for the message
    operation.
    This method should be used as a short hand for the message
    operation.

    @type handlers_map: Dictionary
    @param handlers_map: The map containing the operation
    handlers.
    @rtype: bool
    @return: The result of the notification, useful for some
    types of operations.
    """

    return notify(MESSAGE_VALUE, handlers_map, *arguments, **named_arguments)

def action(handlers_map = None, *arguments, **named_arguments):
    """
    Shortcut method to call the handlers for the action
    operation.
    This method should be used as a short hand for the action
    operation.

    @type handlers_map: Dictionary
    @param handlers_map: The map containing the operation
    handlers.
    @rtype: bool
    @return: The result of the notification, useful for some
    types of operations.
    """

    return notify(ACTION_VALUE, handlers_map, *arguments, **named_arguments)

def progress(handlers_map = None, *arguments, **named_arguments):
    """
    Shortcut method to call the handlers for the progress
    operation.
    This method should be used as a short hand for the progress
    operation.

    @type handlers_map: Dictionary
    @param handlers_map: The map containing the operation
    handlers.
    @rtype: bool
    @return: The result of the notification, useful for some
    types of operations.
    """

    return notify(PROGRESS_VALUE, handlers_map, *arguments, **named_arguments)

def register_g(operation_mame, handler):
    """
    Registers for operations occurring for the provided name
    in the global system scope.

    @type operation_mame: String
    @param operation_mame: The name of the operation for which
    the registration is being done.
    @type handler: Function
    @param handler: The handler to be used in the handling operation
    for the operation with the provided name.
    """

    handlers = GLOBAL_HANDLERS_MAP.get(operation_mame, [])
    handlers.append(handler)
    GLOBAL_HANDLERS_MAP[operation_mame] = handlers

def unregister_g(operation_name, handler = None):
    """
    Unregisters from operations occurring for the provided name
    in the global system scope.

    In case the handler argument is present only the provided
    handler is removed from handling for the operation.

    @type operation_mame: String
    @param operation_mame: The name of the operation for which
    the "unregistration" is being done.
    @type handler: Function
    @param handler: The handler used in the handling operation
    for the operation with the provided name.
    """

    handlers = GLOBAL_HANDLERS_MAP.get(operation_name, [])
    if handler: handlers.remove(handler)
    else: del GLOBAL_HANDLERS_MAP[operation_name]

def notify_g(operation_name, *arguments, **named_arguments):
    """
    Notifies an handler defined in the given handlers map about
    the provided operation.
    The provided arguments are sent to the operation handler
    as parameters.

    This is the global notification and as such the global handlers
    are used for the handling.

    @type operation_name: String
    @param operation_name: The name of the operation to call
    the handler.
    @rtype: bool
    @return: The result of the notification, useful for some
    types of operations.
    """

    return notify(operation_name, None, *arguments, **named_arguments)
