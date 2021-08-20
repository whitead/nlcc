import click

from.utils import text_iter
from .nlp import run_gpt_search
from rich import pretty
from rich.console import Console
from rich.syntax import Syntax
pretty.install()



@click.command()
def main():
    console = Console()
    context = None
    # make a list, so it's pass by ref
    cli_prompt = ['👋']
    for i, query in enumerate(text_iter(cli_prompt)):
            if query.lower() == 'exit' or query.lower() == 'q' or query.lower() == 'quit':
                break
            if query == '':
                context = None
                cli_prompt[0] = '👋'
            elif context is None:
                result, context = run_gpt_search(query, context)
                cli_prompt[0] = '🐍' + context.type + '🐍'
            else:
                result, context = run_gpt_search(query, context)
                console.print(Syntax(context.prompt, 'python', theme='monokai', line_numbers=True))
                console.print(Syntax(result, 'python', theme='monokai', line_numbers=True))
                context.prompt += result + '\n'

