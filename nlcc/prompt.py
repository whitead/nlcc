from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit import print_formatted_text
from enum import Enum


class Modes(Enum):
    QUERY = 0
    TEMPERATURE = 1
    SELECT_NRESPONSE = 2
    WRITE_FILE = 3
    READ_FILE = 4
    SELECT_CONTEXT = 5
    SELECT_RESPONSE = 6
    MULTILINE = 7


class PromptManager:
    def __init__(self):
        self.input_mode = [Modes.SELECT_CONTEXT]
        self.cli_prompt = ['👋']

    def push(self, prompt, mode):
        self.input_mode.append(mode)
        self.cli_prompt.append(prompt)

    def peek_mode(self):
        return self.input_mode[-1]

    def peek_cli_prompt(self):
        return self.cli_prompt[-1]

    def pop(self):
        self.cli_prompt.pop(), self.input_mode.pop()

    def __len__(self):
        return len(self.input_mode)


def text_iter(pm, extra_kbs):

    kb = KeyBindings()
    session = None

    @kb.add('enter')
    def _(event):
        if pm.peek_mode() != Modes.MULTILINE:
            event.current_buffer.validate_and_handle()
        else:
            event.current_buffer.insert_text('\n')

    @kb.add('c-down')
    def _(event):
        if pm.peek_mode() != Modes.MULTILINE:
            pm.push('multiline📜', Modes.MULTILINE)
        else:
            pm.pop()

    @kb.add('escape', 'enter')
    def _(event):
        if pm.peek_mode() == Modes.MULTILINE:
            pm.pop()
            event.current_buffer.validate_and_handle()

    history = InMemoryHistory()
    session = PromptSession(
        history=history,
        auto_suggest=AutoSuggestFromHistory(),
        enable_history_search=True,
        complete_while_typing=True,
        multiline=True,
        rprompt=lambda: f'{pm.peek_mode()}'
        # key_bindings=kb
    )

    def kb_wrapper(fxn):
        def kbf(e):
            fxn(e)
            print_formatted_text('')
        return kbf

    session.key_bindings = kb
    for k, v in extra_kbs.items():
        kb.add(k)(kb_wrapper(v))

    while True:
        q = session.prompt(lambda: f'nlcc|{pm.peek_cli_prompt()}:>')
        yield q
