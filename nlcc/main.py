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
    code = ''
    for i, query in enumerate(text_iter()):
            if query.lower() == 'exit' or query.lower() == 'q' or query.lower == 'quit':
                break
            if query == '':
                code = ''
            result = run_gpt_search(code + query)
            # have to cache selection because vmd sockets are weird
            if result['type'] == 'mdtraj Command':
                code = result['data']
                syntax = Syntax(code, "python", theme="monokai", line_numbers=False)
                console.print(syntax)
