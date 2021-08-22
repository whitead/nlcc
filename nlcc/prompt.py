from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings


def text_iter(cli_prompt, extra_kbs):

    kb = KeyBindings()
    session = None

    @kb.add('enter')
    def _(event):
        event.current_buffer.validate_and_handle()

    @kb.add('escape', 'enter')
    def _(event):
        event.current_buffer.insert_text('\n')

    for k, v in extra_kbs.items():
        kb.add(k)(v)
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
