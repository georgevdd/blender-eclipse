import os
import sys

import bpy
from fileinput import filename

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


def _wrap_norm_path(pydevd_norm_path):
  def _blender_norm_path(filename, normpath):
    """Calculate the real path for a module path reported by Blender.

    When executing code from a script within a .blend file, Blender sets the
    frame's module path to be of the form <blend_file_path>/<text_block_name>
    (even if the script is external).

    PyDev uses its `_NormPath()` function to compute a real filename for code
    loaded from eggs etc, so monkey-patching that is a natural way to add
    support for code from .blend files.

    Args:
      filename: A path to a Python module, e.g. from frame.f_code.co_filename,
          which may refer to a code block within a .blend file.
      normpath: A further path normalisation function (as for
          pydevd_file_utils._NormPath).

    Returns:
      A path to the external file that is associated with the given
      path (if the given path refers to a Blender text block) otherwise the
      result of PyDev's usual _NormPath() path translation mechanism.
    """
    _debug_print('NORM_PATH (0):', filename)
    blend_filename = getattr(bpy.data, 'filepath', ())
    if blend_filename:
      _debug_print('NORM_PATH (1):', blend_filename)
    if filename.startswith(blend_filename):
      text_block_name = filename[len(blend_filename) + 1:]
      _debug_print('NORM_PATH (2):', text_block_name)
      text_block = getattr(bpy.data, 'texts', {}).get(text_block_name)
      if text_block:
        _debug_print('NORM_PATH (3):', text_block.filepath)
        normed_path = pydevd_norm_path(text_block.filepath, normpath)
        _debug_print('NORM_PATH (4):', normed_path)
        return normed_path
    return pydevd_norm_path(filename, normpath)

  return _blender_norm_path

def register():
  _maybe_set_up_debug_logging()
  pydev_src_path = _locate_pydev()
  _ensure_pydev_on_sys_path(pydev_src_path)

  import pydevd_file_utils
  pydevd_file_utils._NormPath = _wrap_norm_path(pydevd_file_utils._NormPath)

  import pydevd
  if 'ECLIPSE_CONNECTOR_DEBUG' in os.environ:
    pydevd.DebugInfoHolder.DEBUG_TRACE_BREAKPOINTS = 1
    pydevd.DebugInfoHolder.DEBUG_TRACE_LEVEL = 3
  pydevd.settrace(suspend=False)


def unregister():
  import pydevd
  pydevd.stoptrace()
