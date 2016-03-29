"""cppstats.

Usage:
  cppstats.py <compile_commands.json>
  cppstats.py <source_file> <clang_arguments>
  cppstats.py (-h | --help)
  cppstats.py --version 

Options:
  -h --help   Show this screen.
  --version   Show version.

"""

from docopt import docopt
import generate_stats
import os

if __name__ == '__main__':
    arguments = docopt(__doc__, version='cppstats 0.1', options_first=True)

    if arguments['<compile_commands.json>']:
        generate_stats.process_compile_commands_db(os.path.abspath(arguments['<compile_commands.json>']))
    else:
        process_source_file(os.path.abspath(arguments['<source_file>']), arguments['<clang_arguments>'])

