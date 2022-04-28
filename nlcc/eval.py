import yaml
from . import nlp
import os
from rich import inspect, reconfigure, get_console
from rich.console import Console
from contextlib import redirect_stdout
from textwrap import dedent
from .timeout import timeout


def eval_single(path, category=None, override_prompt=None, **kwargs):
    with open(path, 'r') as f:
        config = yaml.safe_load(f.read())
    try:
        prompt = nlp.prompts[config['context']
                             ] if override_prompt is None else nlp.prompts[override_prompt]
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
    # TODO Better way?
    # Make it so we can only get one function
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
            with redirect_stdout(None):
                with timeout(seconds=10):
                    exec(dir_string + r + '\n' + test_code, g)
            if 'result' not in g:
                exceptions.append(
                    f'\nYou must have variable `result` defined. \n')
                success = False
            runs.append(g['result'])
        except Exception as e:
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
