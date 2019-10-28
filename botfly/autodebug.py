#!/usr/bin/python3.6

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
Importing this module sets up the Python interpreter to enter the botfly
debugger on an uncaught exception, rather than exiting.

Example:

    def main(argv):
       # ...
       return 0

    # ...
    if __name__ == "__main__":
        from botfly import autodebug
        sys.exit(main(sys.argv))

Normally, if any exception is not caught it results in a stracktrace being
printed at the terminal and the program ending.

After this import, an interactive debugger prompt will be started instead.
"""

import sys

from botfly import debugger

debugger.autodebug()
