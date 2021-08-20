import click

import pyperclip
from.utils import text_iter
from .nlp import Context, run_gpt_search
from rich import pretty
from rich.console import Console
from rich.syntax import Syntax
pretty.install()


def update_temperature(query, codex_temp, gpt3_temp, console):
    try:
        new_codex_temp = float(query.split()[1])
    except (ValueError, IndexError) as e:
            console.print("\tFailed at setting Codex temperature with command:",query)
    if 0 > new_codex_temp or new_codex_temp > 1:
        console.print("\tFailed at setting Codex temperature with command:",query)
        console.print("\tTemperature out of range [0,1]")
    else:
        codex_temp = new_codex_temp
        console.print("\tSetting Codex query temperature to",codex_temp)

    if query.lower().startswith('gpt3-temp'):
        try:
            new_gpt3_temp = float(query.split()[1])
        except (ValueError, IndexError) as e:
            console.print("\tFailed at setting GPT3 temperature with command:",query)
        if 0>new_codex_temp or new_codex_temp>1:
            console.print("\tFailed at setting GPT3 temperature with command:",query)
            console.print("\tTemperature out of range [0,1]")
        else:
            gpt3_temp = new_gpt3_temp
            console.print("\tSetting GPT3 query temperature to",gpt3_temp)
    return codex_temp, gpt3_temp


_DEFAULT_GPT3_T = 0.3
_DEFAULT_CODEX_T = 0.0

@click.command()
@click.option('--auto_context',default=False,is_flag=True,help="Detect a context from my command")
@click.option('--gpt3_temp',default=_DEFAULT_GPT3_T,help="Set the default GPT3 temperature")
@click.option('--codex_temp',default=_DEFAULT_GPT3_T,help="Set the default CODEX temperature")
def main(auto_context,gpt3_temp,codex_temp):
    if gpt3_temp<0 or gpt3_temp>1.0:
        gpt3_temp = _DEFAULT_GPT3_T
        print("Supplied GPT-3 temperature out of bounds, using",gpt3_temp)
    if codex_temp<0 or codex_temp>1.0:
        codex_temp = _DEFAULT_CODEX_T
        print("Supplied CODEX temperature out of bounds, using",codex_temp)

    console = Console()
    context = None
    # make a list, so it's pass by ref
    cli_prompt = ['👋']
    def make_copy(prompt):
        if context is not None:
            pyperclip.copy(context.prompt)
            console.print('\n✨copied✨\n' + prompt, end='')
        else:
            console.print('\n🤔 nothing to copy\n' + prompt, end='')
    for i, query in enumerate(text_iter(cli_prompt, make_copy)):
            if query.lower().startswith('codex-temp') or query.lower().startswith('temperature'):
                codex_temp, gpt3_temp = update_temperature(query, codex_temp, gpt3_temp, console)
                continue
            if query.lower() == 'exit' or query.lower() == 'q' or query.lower() == 'quit':
                break
            if query == 'c':
                context = None
                cli_prompt[0] = '👋'
            elif context is None:
                result, context = run_gpt_search(query, context, auto_context, codex_temp=codex_temp, gpt3_temp=gpt3_temp)
                cli_prompt[0] = '|' + context.type
            else:
                result, context = run_gpt_search(query, context, codex_temp=codex_temp, gpt3_temp=gpt3_temp)
                console.print(Syntax(context.prompt, 'python', theme='monokai', line_numbers=True))
                console.print(Syntax(result, 'python', theme='monokai', line_numbers=True))
                context.prompt += result + '\n'

