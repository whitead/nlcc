import click

import pyperclip
from.utils import text_iter
from .nlp import Context, run_gpt_search
from rich import pretty
from rich.console import Console
from rich.syntax import Syntax
pretty.install()



@click.command()
@click.option('--auto_context',default=False,is_flag=True,help="Detect a context from my command")
def main(auto_context):
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
            if query.lower() == 'exit' or query.lower() == 'q' or query.lower() == 'quit':
                break
            if query == '':
                context = None
                cli_prompt[0] = '👋'
            elif context is None:
                result, context = run_gpt_search(query, context, auto_context)
                cli_prompt[0] = '🐍' + context.type + '🐍'
            else:
                result, context = run_gpt_search(query, context)
                console.print(Syntax(context.prompt, 'python', theme='monokai', line_numbers=True))
                console.print(Syntax(result, 'python', theme='monokai', line_numbers=True))
                context.prompt += result + '\n'

