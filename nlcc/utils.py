from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings


def text_iter(cli_prompt, copy):

    kb = KeyBindings()
    session = None

    @kb.add('enter')
    def _(event):
        event.current_buffer.validate_and_handle()
    @kb.add('escape', 'enter')
    def _(event):
        event.current_buffer.insert_text('\n')
    @kb.add('c-t')
    def _(event):
        copy(f'nlcc{cli_prompt[0]}:>')

    history = InMemoryHistory()
    session = PromptSession(
       history=history,
    auto_suggest=AutoSuggestFromHistory(),
    enable_history_search=True,
    complete_while_typing=True,
    multiline=True,
    key_bindings=kb
    )
    while True:
        q = session.prompt(f'nlcc{cli_prompt[0]}:>')
        yield q