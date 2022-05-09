from pkg_resources import safe_name
import yaml
from . import nlp
import re
import os
from rich import inspect, reconfigure, get_console
from rich.console import Console
from contextlib import redirect_stdout, redirect_stderr, nullcontext, ExitStack
from textwrap import dedent
from .timeout import timeout
import dataclasses


def sanitize(code):
    """Remove things that blow-up the runtime, like exits
    """
    code = code.replace('quit()', 'pass')
    # in case its passing exit codes
    code = re.sub(r'[sy\.]*exit\(.*\)', 'pass', code)
    return code


def eval_single(path, category=None, override_prompt=None, quiet=False, **kwargs):
    with open(path, 'r') as f:
        config = yaml.safe_load(f.read())
    try:
        if override_prompt is None:
            prompt = nlp.prompts[config['context']]
        # special ones
        elif override_prompt == 'insert':
            pkey = config['context'] + '-insert'
            if pkey in nlp.prompts:
                prompt = nlp.prompts[pkey]
            else:
                prompt = nlp.prompts[config['context']]

        elif override_prompt.startswith('header'):
            extra = ''
            if override_prompt.startswith('header-insert:'):
                extra = '-insert'
                header = override_prompt.split('header-insert:')[-1]
            else:
                header = override_prompt.split('header:')[-1]
            pkey = config['context'] + extra
            if pkey in nlp.prompts:
                prompt = nlp.prompts[pkey]
            else:
                prompt = nlp.prompts[config['context']]
            prompt = dataclasses.replace(prompt)
            prompt.text = header + prompt.text
        else:
            prompt = nlp.prompts[override_prompt]
        context = nlp.Context(
            name=config['name'], prompt=prompt)
    except Exception as e:
        print(f'ERROR: Could not parse file {f.name}')
        print(e)
        inspect(config, docs=False, methods=False)
        return None, None

    # this is to short-circuit the evaluator
    # return {'result': np.random.choice([True, False], size=kwargs['n']), 'name': config['name']}, None

    # check if disabled
    disabled = False
    if 'categories' in config:
        if 'disabled' in config['categories']:
            disabled = True
        if category is not None and category not in config['categories']:
            disabled = True
    if disabled:
        return None, None

    dir = os.path.dirname(path)
    with open(os.path.join(dir, config['prompt']), 'r') as f:
        query = f.read()
        # TODO: More transparent way to do this
        if override_prompt is None or 'insert' not in override_prompt:
            query = query.split('[insert]')[0]

    if context.prompt.stop is None:
        context.prompt.stop = ['def']
    elif 'def' not in context.prompt.stop:
        context.prompt.stop = ['def'] + context.prompt.stop
    context = nlp.code_completion(query, context, **kwargs)
    if not 'test' in config or config['test'] is None:
        result = {'name': config['name'], 'context': context, 'result': None}
        return result, ''

    with open(os.path.join(dir, config['test']), 'r') as f:
        test_code = f.read()
    runs = []
    exceptions = []
    dir_string = f"_FILE_DIR_='{dir}'\n"
    markdown = f'\n#### Query\n\n```py\n{context.query}\n\n```'
    for i, r in enumerate(context.responses):
        g = {}
        success = True
        try:
            if quiet:
                cms = redirect_stdout(None), redirect_stderr(
                    None), timeout(seconds=10)
            else:
                cms = (timeout(seconds=10),)
            with ExitStack() as stack:
                for c in cms:
                    stack.enter_context(c)
                exec(dir_string + sanitize(r) + '\n' + test_code, g)
            if 'result' not in g:
                exceptions.append(
                    f'\nYou must have variable `result` defined. \n')
                success = False
            runs.append(g['result'])
        except Exception as e:
            if not quiet:
                print(e)
            exceptions.append(
                f'{str(e)}')
            runs.append(False)
            success = False
        markdown += f'\n#### Run {i}\n\n'
        code_str = r + '\n' + test_code
        markdown += f'```py\n{code_str}\n```\n'
        markdown += f'Output:\n```\n{"Success" if success else exceptions[-1]}\n```\n\n'
    result = {'name': config['name'], 'context': context, 'result': runs}

    # can be too long
    return result, markdown
