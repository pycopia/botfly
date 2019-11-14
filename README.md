# Botfly

An enhanced debugger that uses [prompt-toolkit](https://python-prompt-toolkit.readthedocs.io/en/master/).

Since *prompt-toolkit* is a cross-platform [readline](https://docs.python.org/3/library/readline.html)
replacement it should work on all platforms.

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

## Automatic Debugging

Don't like those annoying uncaught exceptions? Just put the following in your code (during development) to automatically enter the debugger in the event of an uncaught exception.

```python
from botfly import debugger

debugger.autodebug()

...
```

Then if an exception happens that isn't handled you will see the debugger.

