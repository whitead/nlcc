from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory

def text_iter():
    history = InMemoryHistory()
    session = PromptSession(
       history=history,
    auto_suggest=AutoSuggestFromHistory(),
    enable_history_search=True,
    complete_while_typing=True
    )
    while True:
        q = session.prompt('nlcc>')
        yield q