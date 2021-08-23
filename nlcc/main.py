import os
from rich.markdown import Markdown
import pyperclip
from rich.syntax import Syntax
from rich.console import Console
from rich import pretty
from rich import inspect
from .nlp import Context, Prompt, guess_context, code_completion
import click
from importlib_metadata import metadata
from.prompt import text_iter

pretty.install()

def update_temperature(query, code_temp, nlp_temp, console):
    try:
        new_nlp_temp, new_code_temp = [float(s) for s in query.split(',')]
    except (ValueError, IndexError) as e:
        console.print(
            "\tFailed at setting temperature with command:", query)
        return
    if 0 > new_code_temp or new_code_temp > 1:
        console.print(
            "\tFailed at setting code temperature with command:", query)
        console.print("\tTemperature out of range [0,1]")
        return
    else:
        code_temp = new_code_temp
        console.print("\tSetting code🧊 query temperature to", code_temp)

    if 0 > new_code_temp or new_code_temp > 1:
        console.print(
            "\tFailed at setting GPT3 temperature with command:", query)
        console.print("\tTemperature out of range [0,1]")
        return
    else:
        nlp_temp = new_nlp_temp
        console.print("\tSetting GPT3🔥 query temperature to", nlp_temp)
    return code_temp, nlp_temp


_DEFAULT_NLP_T = 0.3
_DEFAULT_CODE_T = 0.0


@click.command()
@click.argument('input_file', default=None, required=False)
@click.option('--n_responses', default=1)
@click.option('--engine', default='openai')
@click.option('--help', is_flag=True)
def main(input_file, engine, help, n_responses):
    console = Console()
    context = None
    adjustTemp = False
    writeFile = False
    loadFile = False
    code_temp, nlp_temp = _DEFAULT_CODE_T, _DEFAULT_NLP_T

    if engine == 'openai':
        console.print('Using OpenAI Engine💰💰💰')
        from .openai import nlp_engine, code_engine
    elif engine == 'huggingface':
        console.print('Using Huggingface Engine')
        from .huggingface import nlp_engine
        from .openai import code_engine
    else:
        console.print('Unkown engine', engine)
        exit(1)

    def query_file_text(input_file, context):
        if not os.path.exists(input_file):
            console.print(f"Input file not found: {input_file}")
            return None
        query = open(input_file,'r').read()
        context = code_completion(query, context, code_engine, T=code_temp, n=n_responses)
        if type(context) == list:
            for idx, response in enumerate(context):
                console.print(f"## Option {idx+1}")
                console.print(Syntax(query, 'python',theme='monokai', line_numbers=True))
                console.print(Syntax(response, 'python',theme='monokai', line_numbers=True))
        else:
            console.print(Syntax(context.text, 'python',theme='monokai', line_numbers=True))
            return context

    if input_file is not None:
        context = Context("",Prompt())
        query_file_text(input_file, context)
        exit()
        

    # make a list, so it's pass by ref
    cli_prompt = ['👋']

    # welcome message
    readme = metadata('nlcc')['Description']
    kb_info = readme.split('## key bindings')[-1]
    help_message = '# 🧠 nlcc 🧠 \n' + '## Info on keybinds\n' + kb_info

    console.print(Markdown(help_message))
    if(help):
        exit()


    def help(e):
        console.print()
        console.print(Markdown(help_message))
        console.print(f'\nnlcc{cli_prompt[0]}:>', end='')

    # make it here to have access to context
    def make_copy(e):
        if context is not None:
            pyperclip.copy(context.text)
            console.print('\n✨copied✨\n' + f'nlcc{cli_prompt[0]}:>', end='')
        else:
            console.print('\n🤔 nothing to copy\n' +
                          f'nlcc{cli_prompt[0]}:>', end='')

    def status(e):
        console.print()
        console.print(Markdown(
            f'# 🧠 nlcc Status 🧠\n ## Parameters\n nlp🔥: `T = {nlp_temp}` \n\n code🧊: `T = {code_temp}`'))
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
            f'\nEnter as 0.7,0.2. Currently nlp🔥:{nlp_temp} code🧊: {code_temp}')
        console.print(f'🔥🧊:>', end='')
        nonlocal adjustTemp
        adjustTemp = True

    def execute(e):
        g = {}
        console.print()
        exec(context.text, g)
        console.print(f'\nnlcc{cli_prompt[0]}:>', end='')
        # pretty.pprint(g)

    def write(e):
        nonlocal writeFile
        writeFile = True
        console.print(f'\nfilename:✍️📝>', end='')

    def load(e):
        nonlocal loadFile
        loadFile = True
        console.print(f'\nfilename:✍️📝>', end='')

    kbs = {'c-w': make_copy, 'c-o': reset_context, 'c-z': execute,
           'c-q': help, 'c-u': status, 'c-t': temperature, 'c-x': write, 'c-l': load}
    for i, query in enumerate(text_iter(cli_prompt, kbs)):
        if query.lower() == 'exit' or query.lower() == 'q' or query.lower() == 'quit':
            break
        elif adjustTemp:
            code_temp, nlp_temp = update_temperature(
                query, code_temp, nlp_temp, console)
            adjustTemp = False
            continue
        elif loadFile:
            if context is None: 
                context = Context("",Prompt())
            context_returned = query_file_text(query, context)
            if type(context_returned) == type(context):
                context = context_returned
            loadFile = False
        elif writeFile:
            if context:
                with open(query, 'w') as f:
                    f.write(context.text + '\n')
                    console.print(
                        f'✨wrote to {query}✨')
            else:
                console.print('🤔 nothing to write')
            writeFile = False

        elif context is None:
            context = guess_context(query, nlp_engine, nlp_temp)
            cli_prompt[0] = '|' + context.name
        else:
            context = code_completion(
                query, context, code_engine, T=code_temp)
            console.print(Syntax(context.text, 'python',
                                 theme='monokai', line_numbers=True))
        # print_header(console, code_temp)
