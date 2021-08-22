from rich.markdown import Markdown
import pyperclip
from rich.syntax import Syntax
from rich.console import Console
from rich import pretty
from rich import inspect
from .nlp import Context, run_gpt_search
import click
from importlib_metadata import metadata
from.prompt import text_iter

pretty.install()


def update_temperature(query, codex_temp, gpt3_temp, console):
    try:
        new_gpt3_temp, new_codex_temp = [float(s) for s in query.split(',')]
    except (ValueError, IndexError) as e:
        console.print(
            "\tFailed at setting temperature with command:", query)
        return
    if 0 > new_codex_temp or new_codex_temp > 1:
        console.print(
            "\tFailed at setting Codex temperature with command:", query)
        console.print("\tTemperature out of range [0,1]")
        return
    else:
        codex_temp = new_codex_temp
        console.print("\tSetting Codex🧊 query temperature to", codex_temp)

    if 0 > new_codex_temp or new_codex_temp > 1:
        console.print(
            "\tFailed at setting GPT3 temperature with command:", query)
        console.print("\tTemperature out of range [0,1]")
        return
    else:
        gpt3_temp = new_gpt3_temp
        console.print("\tSetting GPT3🔥 query temperature to", gpt3_temp)
    return codex_temp, gpt3_temp


_DEFAULT_GPT3_T = 0.3
_DEFAULT_CODEX_T = 0.0


@click.command()
def main():
    console = Console()
    context = None
    adjustTemp = False
    codex_temp, gpt3_temp = _DEFAULT_CODEX_T, _DEFAULT_GPT3_T

    # make a list, so it's pass by ref
    cli_prompt = ['👋']

    # make it here to have access to context
    def make_copy(e):
        if context is not None:
            pyperclip.copy(context.text)
            console.print('\n✨copied✨\n' + f'nlcc{cli_prompt[0]}:>', end='')
        else:
            console.print('\n🤔 nothing to copy\n' +
                          f'nlcc{cli_prompt[0]}:>', end='')
    # welcome message
    readme = metadata('nlcc')['Description']
    kb_info = readme.split('## key bindings')[-1]
    help_message = '# 🧠 nlcc 🧠 \n' + '## Info on keybinds\n' + kb_info

    def help(e):
        console.print()
        console.print(Markdown(help_message))
        console.print(f'\nnlcc{cli_prompt[0]}:>', end='')

    def status(e):
        console.print()
        console.print(Markdown(
            f'# 🧠 nlcc Status 🧠\n ## Parameters\n GPT-3🔥: `T = {gpt3_temp}` \n\n CODEX🧊: `T = {codex_temp}`'))
        if context:
            inspect(context, title='Context',  docs=False)
        console.print(f'\nnlcc{cli_prompt[0]}:>', end='')

    def reset_context(e):
        nonlocal context
        context = None
        cli_prompt[0] = '👋'
        console.print(f'\nnlcc{cli_prompt[0]}:>', end='')

    def temperature(e):
        console.print(
            f'\nEnter as 0.7,0.2. Currently GPT-3🔥:{gpt3_temp} CODEX🧊: {codex_temp}')
        console.print(f'🔥🧊:>', end='')
        nonlocal adjustTemp
        adjustTemp = True

    def execute(e):
        g = {}
        console.print()
        exec(context.text, g)
        console.print(f'\nnlcc{cli_prompt[0]}:>', end='')
        # pretty.pprint(g)

    kbs = {'c-w': make_copy, 'c-o': reset_context, 'c-z': execute,
           'c-q': help, 'c-u': status, 'c-t': temperature}
    for i, query in enumerate(text_iter(cli_prompt, kbs)):
        if query.lower() == 'exit' or query.lower() == 'q' or query.lower() == 'quit':
            break
        elif adjustTemp:
            codex_temp, gpt3_temp = update_temperature(
                query, codex_temp, gpt3_temp, console)
            adjustTemp = False
            continue

        elif context is None:
            result, context = run_gpt_search(
                query, context, codex_temp=codex_temp, gpt3_temp=gpt3_temp)
            cli_prompt[0] = '|' + context.name
        else:
            result, context = run_gpt_search(
                query, context, codex_temp=codex_temp, gpt3_temp=gpt3_temp)
            console.print(Syntax(context.text, 'python',
                                 theme='monokai', line_numbers=True))
        # print_header(console, codex_temp)
