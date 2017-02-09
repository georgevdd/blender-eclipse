# Overview

Blender's Python editor is functional, but not the best available. The
tools and guidelines in this repository are for connecting Blender to
Eclipse, bringing superior tools to bear on your Blender scripts.

These tools build on the instructions on the
[Blender Wiki](https://wiki.blender.org/index.php/Dev:Doc/Tools/Debugging/Python_Eclipse)
and the original [book of Eclipse/Blender instructions](http://airplanes3d.net/downloads/pydev/pydev-blender-en.pdf) by Witold Jaworski.

Advantages include:
* No need to work out exactly where PyDev stores its source code.
* No need to update your scripts when you upgrade PyDev.
* No need to install and maintain a separate Python interpreter.
* Ability to launch Blender directly from within Eclipse.

# Prerequisites

* Install [Blender](http://www.blender.org)
* Install [Eclipse](http://www.eclipse.org)
* Install [PyDev](http://www.pydev.org/) (by adding http://www.pydev.org/updates/ to Eclipse's
Update Manager).

---

NOTE: These instructions assume for the sake of example that Blender
is version 2.77 and that it's installed on OSX at
`/Applications/Blender/blender.app`, but it should not be hard to work
out how to adapt the paths in this document to match your own installation.

---

# Download

`cd path/to/repo ; git clone `[`'https://github.com/georgevdd/blender-eclipse.git'`](https://github.com/georgevdd/blender-eclipse.git)` .`


# Eclipse Setup

These steps should only need to be done once per Eclipse installation.

---

**TODO**: Make an Eclipse plugin that does these steps, or at least
checks that they've been done.

---


## Autocompletion for Blender APIs

1. Fetch the API building script:

`git clone `[`'https://github.com/mutantbob/pycharm-blender.git'`](https://github.com/mutantbob/pycharm-blender.git)` .`

2. Run it within Blender:

`/Applications/Blender/blender.app/Contents/MacOS/blender -b -P python_api/pypredef_gen.py`

This will create a directory called `pypredef` which will be useful
when setting up the Python interpreter, next.

---

**NOTE**: Something that Jaworski's book doesn't mention: You can use `assert
isinstance(x, XType)` or `if isinstance(x, XType):` to help PyDev
reason about the types of variables. With Python 3.5 or later you can use [type hints](https://docs.python.org/3/library/typing.html) too.

---

---

**TODO**: bring `pypredef_gen.py` into this repository and make
  running it easier.

---

## Python Interpreter

The Python interpreter that Eclipse will use needs to be the same
version as the one that Blender uses. The easy way to achieve that is
to set up Eclipse to use the interpreter that comes with Blender:

- Eclipse -> Preferences
  -  PyDev -> Interpreters -> Python Interpreter
    - New ...
      - Interpreter Name: `Blender Python3` or whatever you like
      - Interpreter Executable: `/Applications/Blender/blender.app/Contents/Resources/2.77/python/bin/python3.5m`
      - Click `OK`.
      - PyDev should find the associated `lib` directory. Click `OK` to accept everything it finds in there.
    - Predefined
      - New ...
        - Choose the `pypredef` directory which was created in the
        previous section.


# Eclipse Project Setup

These steps need to be done for each Eclipse PyDev project that you want to
use with Blender.

---

**TODO**: Make an Eclipse plugin that does these steps, or at least
checks that they've been done.

---


## Interpreter

- RClick Project -> Properties
  - PyDev - Interpreter/Grammar
    - Grammar Version: 3.0-3.5 (or whatever is appropriate for the interpreter you're using)
    - Interpreter: `Blender Python3`


## Debugger

- RClick PyBlend -> Run As -> Run Configurations ...
  - RClick C/C++ Application -> New
    - Name: `Blender Subprocess`
    - Main
      - Project: `PyBlend`
      - C/C++ Application: `/Applications/Blender/blender.app/Contents/MacOS/blender`
    - Arguments
      ```
      --window-geometry 960 0 960 10000
      /Users/georgevdd/src/blender/eclipse_blend.blend
      --addons eclipse_connector
      ```

      You can omit the path to a `.blend` file if you'd rather start
      with whatever Blender thinks your default startup file is.
      Also the `--window-geometry` setting is optional; I use it
      to make the Blender window show up where it doesn't cover my
      Eclipse workspace.
    - Environment
      - `PYDEV_SRC_PATH` `${bundle_location:org.python.pydev}/pysrc`
    
        This setting tells the Eclipse Connector for Blender where it
        should find the PyDev source code.
    - Apply

---

NOTE: The new Run Configuration *must* be given a valid "Project" field, otherwise
it will silently not set up its environment variables properly. It's
not clear to me why this is.

---

# Blender Setup

These steps should only need to be done once per Blender installation.

1. Install the Eclipse Connector addon:

```
cd /Users/georgevdd/Library/Application Support/Blender/2.77/scripts/addons
ln -s path/to/repo/eclipse_connector.py .
```


# Usage

1. Make sure the PyDev debugger server is running:
  - Window -> Perspective -> Open Perspective -> Debug
  - PyDev -> Start Debug Server
2. Launch Blender from Eclipse
  - Click on the `PyBlend` project
  - (Run icon) -> Blender Subprocess
  
  Standard output from Blender should appear in the Eclipse console
  view. You should see a small amount of logging from Eclipse
  Connector.
3. Within Blender, when you choose "Run Script" within Blender, control
   will break into the Eclipse debugger when any breakpoint is
   hit. You can now step through your script within the debugger. When
   you choose Resume (F8) within Eclipse, control returns to Blender.
