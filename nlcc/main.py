from enum import Enum
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


class Modes(Enum):
    QUERY = 0
    TEMPERATURE = 1
    SELECT_NRESPONSE = 2
    WRITE_FILE = 3
    READ_FILE = 4
    SELECT_CONTEXT = 5
    SELECT_RESPONSE = 6


def process_n_response(query, console):
    try:
        new_n_responses = int(query)
    except ValueError as e:
        console.print(
            "\tFailed at setting n_responses with value:", query)
        return None
    if 1 > new_n_responses:
        console.print(
            "\tFailed at setting n_responses to value:", new_n_responses)
        console.print("\tn_responses must be an integer >= 1")
        return None
    return new_n_responses


def process_temperature(query, code_temp, nlp_temp, console):
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
    context = Context("", Prompt())
    # it's a list because you could do multiple nested shortcuts
    # and so it can be passed by ref
    input_mode = [Modes.SELECT_CONTEXT]
    cli_prompt = ['👋']
    code_temp, nlp_temp = _DEFAULT_CODE_T, _DEFAULT_NLP_T

    if engine == 'openai':
        console.print('Using OpenAI Engine💰💰💰')
        from .openai import nlp_engine, code_engine
    elif engine == 'huggingface':
        console.print('Using Huggingface Engine🤗🤗🤗')
        from .huggingface import nlp_engine
    else:
        console.print('Unkown engine', engine)
        exit(1)

    def query_file_text(input_file, context):
        if not os.path.exists(input_file):
            console.print(f"Input file not found: {input_file}")
            return None
        query = open(input_file, 'r').read()
        context, response_text = code_completion(
            query, context, code_engine, T=code_temp, n=n_responses)
        if len(response_text) > 1:
            for idx, response in enumerate(context):
                console.print(f"## Option {idx+1}")
                console.print(
                    Syntax(query, context.prompt.language, theme='monokai', line_numbers=True))
                console.print(Syntax(response, context.prompt.language,
                                     theme='monokai', line_numbers=True))
        else:
            console.print(Syntax(context.text, context.prompt.language,
                                 theme='monokai', line_numbers=True))
            return context

    if input_file is not None:
        context = Context("", Prompt())
        query_file_text(input_file, context)
        exit()

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
        console.print(f'\nnlcc{cli_prompt[-1]}:>', end='')

    # make it here to have access to context
    def make_copy(e):
        if context is not None:
            pyperclip.copy(context.text)
            console.print('\n✨copied✨\n' + f'nlcc{cli_prompt[-1]}:>', end='')
        else:
            console.print('\n🤔 nothing to copy\n' +
                          f'nlcc{cli_prompt[-1]}:>', end='')

    def status(e):
        console.print()
        console.print(Markdown(
            f'# 🧠 nlcc Status 🧠\n - nlp🔥: `T = {nlp_temp}` \n- code🧊: `T = {code_temp}` \n- n_responses🤏: `N = {n_responses}` '))
        inspect(context, title='Context',  docs=False)
        if len(input_mode) > 1:
            inspect(input_mode, title='Input Mode', docs=False)
        console.print(f'\nnlcc{cli_prompt[-1]}:>', end='')

    def reset_context(e):
        nonlocal context
        context = Context("", Prompt())
        cli_prompt.append('👋')
        console.print(f'\nnlcc{cli_prompt[-1]}:>', end='')
        input_mode.append(Modes.SELECT_CONTEXT)

    def responses(e):
        cli_prompt.append('|num_responses🥳:')
        console.print(
            "Wow you want more?🥳🥳 How many responses?")
        console.print(f'\nnlcc{cli_prompt[-1]}:>', end='')
        input_mode.append(Modes.SELECT_NRESPONSE)

    def temperature(e):
        cli_prompt.append('|🔥🧊')
        console.print(
            f'\nEnter as 0.7,0.2. Currently nlp🔥:{nlp_temp} code🧊: {code_temp}')
        console.print(f'\nnlcc{cli_prompt[-1]}:>', end='')
        input_mode.append(Modes.TEMPERATURE)

    def execute(e):
        g = {}
        console.print()
        exec(context.text, g)
        console.print(f'\nnlcc{cli_prompt[-1]}:>', end='')
        # pretty.pprint(g)

    def write(e):
        cli_prompt.append('|filename:✍️📝')
        console.print(f'\nnlcc{cli_prompt[-1]}:>', end='')
        input_mode.append(Modes.WRITE_FILE)

    def read(e):
        input_mode.append(Modes.READ_FILE)
        cli_prompt.append('|filename:👀📝')
        console.print(f'\nnlcc{cli_prompt[-1]}:>', end='')

    kbs = {'c-w': make_copy, 'c-o': reset_context, 'c-z': execute, 'c-n': responses,
           'c-q': help, 'c-u': status, 'c-t': temperature, 'c-x': write, 'c-l': read}
    for i, query in enumerate(text_iter(cli_prompt, kbs)):
        if query.lower() == 'exit' or query.lower() == 'q' or query.lower() == 'quit':
            break
        elif input_mode[-1] == Modes.SELECT_NRESPONSE:
            new_n = process_n_response(query, console)
            if new_n is not None:
                n_responses = new_n
        elif input_mode[-1] == Modes.TEMPERATURE:
            new_t = process_temperature(
                query, code_temp, nlp_temp, console)
            if new_t is not None:
                code_temp, nlp_temp = new_t
        elif input_mode[-1] == Modes.SELECT_CONTEXT:
            context = guess_context(query, nlp_engine, nlp_temp)
            cli_prompt.append('|' +
                              context.name if context.name else 'no context')
        elif input_mode[-1] == Modes.READ_FILE:
            context_returned = query_file_text(query, context)
            if type(context_returned) == type(context):
                context = context_returned
        elif input_mode[-1] == Modes.WRITE_FILE:
            if context:
                if query and os.path.normpath('(path-to-wiki)/foo/bar.txt').startswith('(path-to-wiki)'):
                    with open(query, 'w') as f:
                        f.write(context.text + '\n')
                        console.print(
                            f'✨wrote to {query}✨')
                else:
                    console.print(f'🤔 Not sure about this filepath: {query}')
            else:
                console.print('🤔 nothing to write')
        elif input_mode[-1] == Modes.SELECT_RESPONSE:
            try:
                i = int(query) - 1
                context.text = context.responses[i]
                console.print(Syntax(context.text, context.prompt.language,
                                     theme='monokai', line_numbers=True))
                context.responses = None
            except Exception as e:
                console.print(e)
                console.print('🤮 what was that? Please pick response')
                continue
        else:
            context = code_completion(
                query, context, code_engine, T=code_temp, n=n_responses)
            if len(context.responses) == 1:
                context.text = context.responses[0]
                console.print(Syntax(context.text, context.prompt.language,
                                     theme='monokai', line_numbers=True))
                context.responses = None
            else:
                for ridx, r in enumerate(context.responses):
                    console.print(f"## Option {ridx+1}")
                    console.print(Syntax(r, context.prompt.language,
                                         theme='monokai', line_numbers=True))
                input_mode.append(Modes.SELECT_RESPONSE)
                cli_prompt.append('🤔which response')
                # do not want pop
                continue

        # reset mode
        input_mode.pop()
        cli_prompt.pop()
        if len(input_mode) == 0:
            input_mode.append(Modes.QUERY)
            cli_prompt.append('|' +
                              context.name if context.name else 'no context')
