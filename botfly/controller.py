# python3

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Controller component module.
"""

__all__ = ['CommandController']

import sys

from prompt_toolkit.completion import DummyCompleter

from . import commands
from . import exceptions
from . import docopt


class CommandController:
    """Controller wraps a UI and object with commands.

    Manageds completion scopes, calling methods on commands and dealing with
    errors.

    Provides built-in docopt support. The method's docstring is inspected for
    *Usage:* section and arguments parsed, with the argument dictionary passed as
    parameter to to command method.

    With our without a *Usage* section, the arguments will have an "argv" key
    referencing the original argv value from the parser.
    """
    def __init__(self, commands):
        self.commands = commands
        self._completion_scopes = {}
        self._command_list = None
        self._ui = commands._ui
        self.environ = self._ui.environ

    # Overrideable exception hook method - do something with command exceptions.
    def except_hook(self, ex, val, tb):
        self._ui.error("{}: {}".format(ex.__name__, val))

    # Override this if your subcommand passes something useful back
    # via a parameter to the CommandQuit exception.
    def handle_subcommand_exit(self, value):
        pass

    def finalize(self):
        self.commands.finalize()

    # completer management methods
    def add_completion_scope(self, name, completer):
        self._completion_scopes[name] = completer

    def get_completion_scope(self, name):
        return self._completion_scopes.get(name, DummyCompleter())

    def remove_completion_scope(self, name):
        del self._completion_scopes[name]

    def getarg(self, argv, index, default=None):
        return argv[index] if len(argv) > index else default

    def call(self, argv):
        """Dispatch command method by calling with an argv that has the method
        name as first element.
        """
        if not argv or not argv[0] or argv[0].startswith("_"):
            return 2
        argv = self._expand_aliases(argv)
        if argv[0].startswith("#"):  # A comment
            return 0
        # ok, now fetch the real method...
        meth = getattr(self.commands, argv[0],
                       self.commands.default_command)
        try:
            arguments = docopt.docopt(meth.__doc__,
                                      argv=argv[1:],
                                      help=False, version=None,
                                      options_first=True)
            arguments["argv"] = argv
        except docopt.DocoptLanguageError:
            arguments = {"argv": argv}
        except docopt.DocoptExit as docerr:
            self._ui.warning(str(docerr))
            return 2
        # ...and exec it.
        try:
            rv = meth(arguments)  # call the method with arguments dict
        except (exceptions.NewCommand,
                exceptions.CommandQuit,
                exceptions.CommandExit,
                KeyboardInterrupt):
            raise  # pass these through to parser
        except:  # noqa
            ex, val, tb = sys.exc_info()
            self.except_hook(ex, val, tb)
        else:
            if rv is not None:
                try:
                    self._ui.environ["?"] = int(rv)
                except (ValueError, TypeError, AttributeError):
                    self._ui.environ["?"] = 0
                self._ui.environ["_"] = rv
            return rv

    def _expand_aliases(self, argv):
        seen = {}
        while 1:
            alias = self.commands._aliases.get(argv[0], None)
            if alias:
                if alias[0] in seen:
                    break  # alias loop
                seen[alias[0]] = True
                # do the substitution
                del argv[0]
                rl = alias[:]
                rl.reverse()
                for arg in rl:
                    argv.insert(0, arg)
            else:
                break
        return argv

    def get_command_names(self):
        if self._command_list is None:
            self._command_list = commands.get_command_list(self.commands)
        return self._command_list
