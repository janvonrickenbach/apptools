#!/usr/bin/env python

#------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Riverbank Computing Limited
# Description: <Enthought permissions package component>
#------------------------------------------------------------------------------


# Standard library imports.
import errno
import optparse
import socket
import sys
import xmlrpclib


# The default IP address to connect to.
DEFAULT_ADDR = socket.gethostbyname(socket.gethostname())

# The default port to connect to.
DEFAULT_PORT = 3800


def check_name(opts):
    """Check the name was specified with the --name flag and return the value.
    """

    if not opts.name:
        raise Exception("the --name flag to specify a name")

    return opts.name


def check_password(opts):
    """Check the password was specified with the --password flag and return the
    value."""

    if not opts.password:
        raise Exception("the --password flag to specify a password")

    return opts.password


def add_role(opts):
    """Add a new role."""

    return ([check_name(opts), opts.description, opts.permissions, opts.key],
            ['Status'])


def add_user(opts):
    """Add a new user."""

    return ([check_name(opts), opts.description, check_password(opts),
                    opts.key],
            ['Status'])


def get_user(opts):
    """Get the details of a user."""

    return ([check_name(opts), opts.key],
            ['Name', 'Description', 'Blob', 'Password'])


def is_empty_policy(opts):
    """Check if there is any policy data."""

    return ([], ['Policy is empty'])


# The list of actions that can be invoked from the command line.
actions = [
    add_role,
    add_user,
    get_user,
    is_empty_policy,
]


def store_list(option, opt_str, value, p):
    """An option parser callback that converts space separated words into a
    list of strings."""

    setattr(p.values, option.dest, value.split(' '))


# Parse the command line.
p = optparse.OptionParser(usage="%prog [options] action", description="This "
        "is a client used to test the XML-RPC server.  The following actions "
        "are supported: %s" % ', '.join([a.func_name for a in actions]))

p.add_option('--ip-address', default=DEFAULT_ADDR, dest='addr',
        help="the IP address to connect to [default: %s]" % DEFAULT_ADDR)
p.add_option('-d', '--description', default='', dest='description',
        help="a description (used by add_role, add_user)")
p.add_option('-k', '--key', default='', dest='key',
        help="the session key returned by login (used by add_role, add_user, "
                "get_user)")
p.add_option('-n', '--name', dest='name',
        help="a name (used by add_role, add_user, get_user)")
p.add_option('--permissions', action='callback', callback=store_list,
        default=[], dest='permissions', type='string',
        help="a space separated list of permission names (used by add_role)")
p.add_option('-p', '--password', dest='password',
        help="a password (used by add_user)")
p.add_option('--port', type='int', default=DEFAULT_PORT, dest='port',
        help="the TCP port to connect to [default: %d]" % DEFAULT_PORT)
p.add_option('-v', '--verbose', action='store_true', default=False,
        dest='verbose', help="display the progress of the RPC")

opts, args = p.parse_args()

if len(args) != 1:
    p.error("exactly one action must be given")

for action in actions:
    if action.func_name == args[0]:
        break
else:
    p.error("unknown action: %s" % args[0])

# Get the action's arguments.
try:
    action_args, result_names = action(opts)
except Exception, e:
    sys.stderr.write("The %s action requires %s\n" % (action.func_name, e))
    sys.exit(2)

# Create the proxy.
proxy = xmlrpclib.ServerProxy(uri='http://%s:%d' % (opts.addr, opts.port),
        verbose=opts.verbose)

try:
    result = getattr(proxy, action.func_name)(*action_args)
except socket.error, e:
    err, msg = e.args

    if err == errno.ECONNREFUSED:
        sys.stderr.write("Unable to connect to permissions server at %s:%d\n" % (opts.addr, opts.port))
    else:
        sys.stderr.write("socket error: %s\n" % msg)

    sys.exit(1)
except xmlrpclib.Fault, e:
    # Extract the text of the exception.  If we don't recognise the format then
    # display the lot.
    tail = e.faultString.find(':')
    if tail < 0:
        msg = e.faultString
    else:
        msg = e.faultString[tail + 1:]

    print "The call raised an exception: %s" % msg
    sys.exit(0)

# Show the result.
nr_names = len(result_names)

try:
    nr_values = len(result)
except TypeError:
    nr_values = 1
    result = [result]

if nr_names != nr_values:
    print "Expected %d result values but received %d" % (nr_names, nr_values)

for i in range(nr_names, nr_values):
    result_names.append("Result %d" % i)

for i in range(nr_values, nr_names):
    result.append("Result missing")

width = 1
for i, name in enumerate(result_names):
    name += ':'

    if width < len(name):
        width = len(name)

    result_names[i] = name

for name, value in zip(result_names, result):
    print "%-*s %s" % (width, name, value)
