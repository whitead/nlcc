# nlcc
[![PyPI version](https://badge.fury.io/py/nlcc.svg)](https://badge.fury.io/py/nlcc)[![tests](https://github.com/whitead/nlcc/actions/workflows/tests.yml/badge.svg)](https://github.com/whitead/nlcc)

![Demo](./docs/demo.svg)

## Install

```sh
pip install nlcc
```

Must have Open-AI Codex key: `export OPENAI_API_KEY=<your key here>`
then `nlcc`

## citation

Please cite [our preprint](https://arxiv.org/abs/2108.13360)

```bibtex
@article{hocky2021natural,
  title={Natural Language Processing Models That Automate Programming Will Transform Chemistry Research and Teaching},
  author={Hocky, Glen M and White, Andrew D},
  journal={arXiv preprint arXiv:2108.13360},
  year={2021}
}
```

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
