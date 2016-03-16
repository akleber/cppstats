venv setup
----------

https://docs.python.org/3/library/venv.html
http://stackoverflow.com/questions/1783146/where-in-a-virtualenv-does-my-code-go


Commands

::

   mkdir venvs
   cd venvs
   pyvenv cppstats
   source cppstats/bin/activate
   cd ..
   mkdir cppstats


For Sublimetext 2 integration see cppstats.sublime-project


Additional pip3 packages
------------------------

-see requirements.txt


Directory structure
-------------------

http://docs.python-guide.org/en/latest/writing/structure/


clang python binding
--------------------

Seems not to be compatible with python 3.5.1, so I used cindex.py from https://bitbucket.org/Anteru/python3-libclang




Learning objectives
-------------------

- project setup
- docstring
- reStructuredText http://docutils.sourceforge.net/docs/user/rst/quickref.html#literal-blocks
- Python 3.5 venv
- multiple processes
- unit tests
- libclang python binding
  - http://eli.thegreenplace.net/2011/07/03/parsing-c-in-python-with-clang
  - http://szelei.me/code-generator/