#!/usr/bin/python

#----------------------------------------------------------------------
# Derived from the LLDB command template available here:
# github.com/mattkelly/lldb-cmd-template
#----------------------------------------------------------------------

import lldb
import commands
import argparse
import shlex


def create_offsets_options():
    usage = "usage: %(prog)s <struct_name>"
    description = '''Dump the offsets of all members of a struct
'''
    parser = argparse.ArgumentParser(
        description=description,
        prog='offsets',
        usage=usage)
    parser.add_argument(
        'struct_name',
        help='The name of the struct to dump member offsets for')
    return parser

def dump_address_node(node, depth):
    node_type = node.GetType()
    node_type_str = node_type.GetName()
    node_type_resolved_str = ''
    if node_type.IsTypedefType():
        node_type_str = node_type_str.replace('typedef ', '')
        node_type_resolved_str = ' [{}]'.format(node_type.GetTypedefedType().GetName())

    print '{}{} ({}{}): {}'.format(' ' * 4 * depth,
            node.GetName(),
            node_type_str, node_type_resolved_str,
            node.GetAddress())

def dump_address_tree(node, depth):
    dump_address_node(node, depth)

    num_children = node.GetNumChildren()
    if num_children == 0:
        pass
    elif not node.GetType().IsArrayType():
        for i in range(num_children):
            child = node.GetChildAtIndex(i)
            dump_address_tree(child, depth + 1)

def the_offsets_command(debugger, command, result, dict):
    # Use the Shell Lexer to properly parse up command options just like a
    # shell would
    command_args = shlex.split(command)
    parser = create_offsets_options()
    try:
        args = parser.parse_args(command_args)
    except:
        # if you don't handle exceptions, passing an incorrect argument to the ArgumentParser will cause LLDB to exit
        # (courtesy of argparse dealing with argument errors by throwing SystemExit)
        result.SetError("option parsing failed")
        return

    # in a command - the lldb.* convenience variables are not to be used
    # and their values (if any) are undefined
    # this is the best practice to access those objects from within a command
    target = debugger.GetSelectedTarget()
    process = target.GetProcess()
    thread = process.GetSelectedThread()
    frame = thread.GetSelectedFrame()
    if not frame.IsValid():
        return "no frame here"

    struct_value = frame.FindVariable(args.struct_name)
    dump_address_tree(struct_value, 0)

def __lldb_init_module(debugger, dict):
    # This initializer is being run from LLDB in the embedded command interpreter
    # Make the options so we can generate the help text for the new LLDB
    # command line command prior to registering it with LLDB below
    parser = create_offsets_options()
    the_offsets_command.__doc__ = parser.format_help()
    # Add any commands contained in this module to LLDB
    debugger.HandleCommand(
        'command script add -f offsets.the_offsets_command offsets')
    print 'The "offsets" command has been installed, type "help offsets" or "offsets --help" for detailed help.'
