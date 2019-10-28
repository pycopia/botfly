#!/usr/bin/python3

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
User Interface base classes and themes.
"""

__all__ = ['UserInterface']

import os
import sys
import time
import textwrap
from pprint import PrettyPrinter

from .fsm import FSM, ANY

PROMPT_START_IGNORE = '\001'
PROMPT_END_IGNORE = '\002'


class UserInterface:
    """An ANSI terminal user interface for CLIs.  """
    def __init__(self, io, theme):
        self._io = io
        self.environ = os.environ.copy()
        self.environ["_"] = None
        self._cache = {}
        self._initfsm()
        self._printer = PrettyPrinter(indent=1, width=self._io.columns,
                                      depth=None, stream=self._io, compact=False)

    @property
    def columns(self):
        return self._io.columns

    @property
    def rows(self):
        return self._io.rows

    def close(self):
        if self._io is not None:
            self._io.close()
            self._io = None

    def clone(self, theme=None):
        return self.__class__(self._io, self.environ.copy(), theme or self._theme)

    def print(self, *objs, **kwargs):
        self._io.print(*objs, **kwargs)

    def pprint(self, obj):
        self._printer.pprint(obj)

    def print_obj(self, obj, nl=1):
        self._io.write(str(obj))
        if nl:
            self._io.write("\n")
        self._io.flush()

    def write(self, text):
        return self._io.write(text)

    def writeerror(self, text):
        return self._io.error(text)

    def printf(self, text):
        "Print text run through the expansion formatter."
        self.write(self.prompt_format(text))

    def error(self, text):
        self.printf("%r{}%N\n".format(text))

    def warning(self, text):
        self.printf("%Y{}%N\n".format(text))

    # user input
    def _get_prompt(self, name, prompt=None):
        return self._input_prompt_format(prompt or self.environ[name])

    def _input_prompt_format(self, ps):
        self._fsm.process_string(ps)
        return self._getarg()

    def user_input(self, prompt=None):
        return self._io.input(self._get_prompt("PS1", prompt))

    def more_user_input(self):
        return self._io.input(self._get_prompt("PS2"))

    def yes_no(self, prompt, default=True):
        while 1:
            yesno = get_input(self.prompt_format(prompt),
                              "Y" if default else "N",
                              self._io.input)
            yesno = yesno.upper()
            if yesno.startswith("Y"):
                return True
            elif yesno.startswith("N"):
                return False
            else:
                self.print("Please enter yes or no.")

    def _format_doc(self, s, color):
        i = s.find("\n")
        if i > 0:
            return (color + s[:i] +
                    self._theme.NORMAL +
                    textwrap.indent(textwrap.dedent(self.prompt_format(s[i:])), "  ") +
                    "\n")
        else:
            return color + s + self._theme.NORMAL + "\n"

    def print_doc(self, doc):
        self.print(self._format_doc(doc, self._theme.help_text))

    def prompt_format(self, ps):
        "Expand percent-exansions in a string and return the result."
        self._ffsm.process_string(ps)
        if self._ffsm.arg:
            arg = self._ffsm.arg
            self._ffsm.arg = ''
            return arg
        else:
            return None

    def register_expansion(self, key, func):
        """Register a percent-expansion function.
        The function must take one argument, and return a string. The argument is
        the character expanded on.
        """
        key = str(key)[0]
        if key not in self._PROMPT_EXPANSIONS:
            self._PROMPT_EXPANSIONS[key] = func
            self._FORMAT_EXPANSIONS[key] = func
        else:
            raise ValueError("expansion key !r{} already exists.".format(key))

    def unregister_expansion(self, key):
        key = str(key)[0]
        try:
            del self._PROMPT_EXPANSIONS[key]
            del self._FORMAT_EXPANSIONS[key]
        except KeyError:
            pass

    # FSM for prompt expansion
    def _initfsm(self):
        # maps percent-expansion items to some value.
        theme = self._theme
        # Used in prompt strings given to readline library.
        self._PROMPT_EXPANSIONS = {
            "I": PROMPT_START_IGNORE + theme.BRIGHT + PROMPT_END_IGNORE,
            "N": PROMPT_START_IGNORE + theme.NORMAL + PROMPT_END_IGNORE,
            "D": PROMPT_START_IGNORE + theme.DEFAULT + PROMPT_END_IGNORE,
            "R": PROMPT_START_IGNORE + theme.BRIGHTRED + PROMPT_END_IGNORE,
            "G": PROMPT_START_IGNORE + theme.BRIGHTGREEN + PROMPT_END_IGNORE,
            "Y": PROMPT_START_IGNORE + theme.BRIGHTYELLOW + PROMPT_END_IGNORE,
            "B": PROMPT_START_IGNORE + theme.BRIGHTBLUE + PROMPT_END_IGNORE,
            "M": PROMPT_START_IGNORE + theme.BRIGHTMAGENTA + PROMPT_END_IGNORE,
            "C": PROMPT_START_IGNORE + theme.BRIGHTCYAN + PROMPT_END_IGNORE,
            "W": PROMPT_START_IGNORE + theme.BRIGHTWHITE + PROMPT_END_IGNORE,
            "r": PROMPT_START_IGNORE + theme.RED + PROMPT_END_IGNORE,
            "g": PROMPT_START_IGNORE + theme.GREEN + PROMPT_END_IGNORE,
            "y": PROMPT_START_IGNORE + theme.YELLOW + PROMPT_END_IGNORE,
            "b": PROMPT_START_IGNORE + theme.BLUE + PROMPT_END_IGNORE,
            "m": PROMPT_START_IGNORE + theme.MAGENTA + PROMPT_END_IGNORE,
            "c": PROMPT_START_IGNORE + theme.CYAN + PROMPT_END_IGNORE,
            "w": PROMPT_START_IGNORE + theme.WHITE + PROMPT_END_IGNORE,
            "n": "\n",
            "h": self._hostname,
            "u": self._username,
            "d": self._cwd,
            "L": self._shlvl,
            "t": self._time,
            "T": self._date,
        }

        self._FORMAT_EXPANSIONS = {
            "I": theme.BRIGHT,
            "N": theme.NORMAL,
            "D": theme.DEFAULT,
            "R": theme.BRIGHTRED,
            "G": theme.BRIGHTGREEN,
            "Y": theme.BRIGHTYELLOW,
            "B": theme.BRIGHTBLUE,
            "M": theme.BRIGHTMAGENTA,
            "C": theme.BRIGHTCYAN,
            "W": theme.BRIGHTWHITE,
            "r": theme.RED,
            "g": theme.GREEN,
            "y": theme.YELLOW,
            "b": theme.BLUE,
            "m": theme.MAGENTA,
            "c": theme.CYAN,
            "w": theme.WHITE,
            "n": "\n",
            "h": self._hostname,
            "u": self._username,
            "d": self._cwd,
            "L": self._shlvl,
            "t": self._time,
            "T": self._date,
        }

        fp = FSM(0)
        self._fsmstates(fp)
        self._fsm = fp

        ff = FSM(0)
        self._fsmstates(ff)
        self._ffsm = ff

    def _fsmstates(self, fsm):
        fsm.add_default_transition(self._error, 0)
        # add text to args
        fsm.add_transition(ANY, 0, self._addtext, 0)
        # percent escapes
        fsm.add_transition("%", 0, None, 1)
        fsm.add_transition("%", 1, self._addtext, 0)
        fsm.add_transition("{", 1, self._startvar, 2)
        fsm.add_transition("}", 2, self._endvar, 0)
        fsm.add_transition("[", 1, None, 3)
        fsm.add_transition("F", 3, self._startfg, 4)
        fsm.add_transition("B", 3, self._startbg, 5)
        fsm.add_transitions("0123456789", 3, self._startfgd, 4)
        fsm.add_transitions("0123456789", 4, self._fgnum, 4)
        fsm.add_transitions("0123456789", 5, self._bgnum, 5)
        fsm.add_transition("]", 4, self._setfg, 0)
        fsm.add_transition("]", 5, self._setbg, 0)
        fsm.add_transition(ANY, 2, self._vartext, 2)
        fsm.add_transition(ANY, 1, self._prompt_expand, 0)
        fsm.arg = ''

    def _startvar(self, c, fsm):
        fsm.varname = ""

    def _vartext(self, c, fsm):
        fsm.varname += c

    def _endvar(self, c, fsm):
        fsm.arg += str(self.environ.get(fsm.varname, fsm.varname))

    def _startbg(self, c, fsm):
        fsm.bgcol = ""

    def _startfg(self, c, fsm):
        fsm.fgcol = ""

    def _startfgd(self, c, fsm):
        fsm.fgcol = c

    def _fgnum(self, c, fsm):
        fsm.fgcol += c

    def _bgnum(self, c, fsm):
        fsm.bgcol += c

    def _setfg(self, c, fsm):
        fsm.arg += (PROMPT_START_IGNORE + "\x1b[38;5;" + fsm.fgcol + "m" + PROMPT_END_IGNORE)

    def _setbg(self, c, fsm):
        fsm.arg += (PROMPT_START_IGNORE + "\x1b[48;5;" + fsm.bgcol + "m" + PROMPT_END_IGNORE)

    def _prompt_expand(self, c, fsm):
        return self._expand(c, fsm, self._PROMPT_EXPANSIONS)

    def _format_expand(self, c, fsm):
        return self._expand(c, fsm, self._FORMAT_EXPANSIONS)

    def _expand(self, c, fsm, mapping):
        try:
            arg = self._cache[c]
        except KeyError:
            try:
                arg = mapping[c]
            except KeyError:
                arg = c
            else:
                if callable(arg):
                    arg = str(arg(c))
        fsm.arg += arg

    def _username(self, c):
        un = os.environ.get("USERNAME") or os.environ.get("USER")
        if un:
            self._cache[c] = un
        return un

    def _shlvl(self, c):
        return str(self.environ.get("SHLVL", ""))

    def _hostname(self, c):
        hn = os.uname()[1]
        self._cache[c] = hn
        return hn

    def _cwd(self, c):
        return os.getcwd()

    def _time(self, c):
        return time.strftime("%H:%M:%S", time.localtime())

    def _date(self, c):
        return time.strftime("%m/%d/%Y", time.localtime())

    def _error(self, input_symbol, fsm):
        print('Prompt string error: {}\n{!r}'.format(input_symbol), file=sys.stderr)
        fsm.reset()

    def _addtext(self, c, fsm):
        fsm.arg += c

    def _getarg(self):
        if self._fsm.arg:
            arg = self._fsm.arg
            self._fsm.arg = ''
            return arg
        else:
            return None


def get_input(prompt="", default=None, input=input):
    """Get user input with an optional default value."""
    if default is not None:
        ri = input("{} [{}]> ".format(prompt, default))
        if not ri:
            return default
        else:
            return ri
    else:
        return input("{}> ".format(prompt))
