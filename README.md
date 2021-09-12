# nlcc
[![PyPI version](https://badge.fury.io/py/nlcc.svg)](https://badge.fury.io/py/nlcc)

![Demo](./docs/demo.svg)

## Install

```sh
pip install nlcc
```

Must have Open-AI Codex key: `export OPENAI_API_KEY=<your key here>`
then `nlcc`

## key bindings

* `ctrl-w` copy to clipboard (Note, you may need to install xsel on linux)
* `ctrl-q` help
* `ctrl-o` reset context
* `ctrl-z` execute python code
* `ctrl-t` adjust temperature
* `ctrl-u` status
* `ctrl-c` quit
* `ctrl-x` write to file (same output as copy to clipboard)
* `ctrl-l` load from file
* `ctrl-n` update number of code responses
* `ctrl-down` Enter multiline. `escape-enter` to enter prompt or `ctrl-down` to leave
