Botfly Debugger Manual
======================

An enhanced debugger that uses `prompt-toolkit`_.

Since *prompt-toolkit* is a cross-platform readline_ replacement it should work on all platforms.

You can also import the `botfly.debugger` module in your code and call the
`post_mortem` function, as with *pdb*.

Some notable features:

* Colorized UI - stacktrace, prompt, etc.
* More informative reports, prompt shows current position in stack.
* Invoke your editor at current point.
* REPL-like evaluator
* Enter sub-REPL if desired.
* Display opcodes.
* Switch to different stack in context or cause exceptions.
* Debug co-routines.

Usage
-----

TODO

.. toctree::
   :maxdepth: 2
   :caption: Contents:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _`prompt-toolkit`: https://python-prompt-toolkit.readthedocs.io/en/master/
.. _readline: https://docs.python.org/3/library/readline.html
