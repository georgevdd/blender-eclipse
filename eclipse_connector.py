import os
import sys

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


def register():
  pydev_src_path = _locate_pydev()
  _ensure_pydev_on_sys_path(pydev_src_path)

  import pydevd
  pydevd.settrace(suspend=False)


def unregister():
  import pydevd
  pydevd.stoptrace()
