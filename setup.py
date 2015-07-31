import sys
from cx_Freeze import setup, Executable
build_exe_options = {"packages": ["os"], "includes": ['firebirdsql','PyQt4','PyQt4']}
base = None
#if sys.platform == "win32":
base = "Win32GUI"
setup( name = "SCF",
version = "1.0",
description = "SCF Manager agent",
options = {"build_exe": build_exe_options},
executables = [Executable("C:\Python34\Scripts\SCF.py", base=base)])
