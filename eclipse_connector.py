import os
import sys

import bpy

bl_info = {
    "name": "Eclipse Connector",
    "description": "Support for editing and debugging scripts using Eclipse.",
    "author": "George van den Driessche",
    "version": (0, 1),
# TODO(georgevdd): Earlier versions than 2.77 ought to work too, but haven't been tested.
    "blender": (2, 77, 0),
    "support": "COMMUNITY",
    "category": "Development"
    }


def _dump_startup_info():
  """Debug spew that can be useful when hacking on this module."""
  print("=== ENV")
  for k in sorted(list(os.environ)):
    print(k, os.environ[k])
  print('=== PATH')
  for p in sorted(sys.path):
    print(p)
  print('=== ARGS')
  for a in sys.argv:
    print(a)


def _locate_pydev():
  try:
    pydev_src_path = os.environ['PYDEV_SRC_PATH']
  except KeyError as e:
    raise EnvironmentError(
      'PYDEV_SRC_PATH should have been set by Eclipse Run Configuration')
  if not os.path.isdir(pydev_src_path):
    raise EnvironmentError("'{}' is not a directory".format(pydev_src_path))
  return pydev_src_path


def _ensure_pydev_on_sys_path(pydev_src_path):
  if pydev_src_path not in sys.path:
    print(
      "Eclipse Connector: Adding pydev source directory '{}' to sys.path ..."
      .format(pydev_src_path))
    sys.path.append(pydev_src_path)
  else:
    print(
      "Eclipse Connector: pydev source directory '{}' is already on sys.path."
      .format(pydev_src_path))


def _debug_print(*args, **kwargs):
  pass


def _maybe_set_up_debug_logging():
  if 'ECLIPSE_CONNECTOR_DEBUG' in os.environ:
    global _debug_print
    _debug_print = print


def _wrap_norm_file_to_server(original_norm_file_to_server):
  def _norm_file_to_server(path):
    """Translates Eclipse breakpoint filepaths to Blender breakpoint filepaths.

    When setting breakpoints, PyDev uses its `norm_file_to_server()` function
    to translate a Python module path from that seen by Eclipse to that
    required by a remote debugger. But Blender expects the module path of a text
    block (even if it's external) to be of the form
    <blend_file_path>/<text_block_name>.

    Monkey-patching norm_file_to_server() allows translation into Blender's
    internal module naming scheme, so that breakpoints set within Eclipse work
    as expected.

    Args:
      path: A path to a Python module

    Returns:
      A path to the Blender text block that is associated with the given
      path (if there is such a text block), otherwise the result of PyDev's
      usual client-to-server path translation mechanism.
    """
    server_path = original_norm_file_to_server(path)
    _debug_print('NORM_FILE_TO_SERVER (1):', path, '->', server_path)
    for text in getattr(bpy.data, 'texts', ()):
      if text.filepath == server_path:
        blender_path = bpy.data.filepath + os.path.sep + text.name
        _debug_print('NORM_FILE_TO_SERVER (2):', server_path, '->', blender_path)
        return blender_path
    return server_path
  return _norm_file_to_server


def register():
  _maybe_set_up_debug_logging()
  pydev_src_path = _locate_pydev()
  _ensure_pydev_on_sys_path(pydev_src_path)

  import pydevd_file_utils
  pydevd_file_utils.norm_file_to_server = _wrap_norm_file_to_server(
      pydevd_file_utils.norm_file_to_server)

  import pydevd
  if 'ECLIPSE_CONNECTOR_DEBUG' in os.environ:
    pydevd.DebugInfoHolder.DEBUG_TRACE_BREAKPOINTS = 1
    pydevd.DebugInfoHolder.DEBUG_TRACE_LEVEL = 3
  pydevd.settrace(suspend=False)


def unregister():
  import pydevd
  pydevd.stoptrace()
