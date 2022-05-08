# nlcc
[![PyPI version](https://badge.fury.io/py/nlcc.svg)](https://badge.fury.io/py/nlcc)[![tests](https://github.com/whitead/nlcc/actions/workflows/tests.yml/badge.svg)](https://github.com/whitead/nlcc)

[![Demo](./docs/demo.svg)](https://github.com/whitead/nlcc/docs/demo.svg)

## Install

```sh
pip install nlcc
```

You must have either an OpenAI Codex key or HuggingFace API key (minimum plan level is Community Pro). Make sure they are set via
`export OPENAI_API_KEY=<your key here>` or `export HUGGINGFACE_API_KEY=<your key here>`
then `nlcc`

## citation

Please cite [our preprint](https://arxiv.org/abs/2108.13360)

```bibtex
@article{hocky2022natural,
  title={Natural language processing models that automate programming will transform chemistry research and teaching},
  author={Hocky, Glen M and White, Andrew D},
  journal={Digital Discovery},
  year={2022},
  publisher={Royal Society of Chemistry}
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
* `[insert]` Add this to your multiline prompt to have completion inserted in a specific location
