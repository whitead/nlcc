import yaml
from . import nlp
import os
from rich import inspect, reconfigure, get_console
from rich.console import Console


def eval_single(path, **kwargs):
    with open(path, 'r') as f:
        config = yaml.safe_load(f.read())
    try:
        context = nlp.Context(
            name=config['name'], prompt=nlp.prompts[config['context']])
    except Exception as e:
        print(f'ERROR: Could not parse file {f.name}')
        print(e)
        inspect(config, docs=False, methods=False)
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

    # check if disabled
    disabled = False
    if 'categories' in config and 'disabled' in config['categories']:
        disabled = True

    if disabled or not 'test' in config or config['test'] is None:
        result = {'name': config['name'], 'context': context, 'result': None}
        return result, ""

    with open(os.path.join(dir, config['test']), 'r') as f:
        test_code = f.read()
    runs = []
    exceptions = []
    dir_string = f"_FILE_DIR_='{dir}'\n"
    for i, r in enumerate(context.responses):
        g = {}
        try:
            exec(dir_string + r + '\n' + test_code, g)
            if 'result' not in g:
                exceptions.append(
                    f'\n### Exception on response {i}\n You must have variable `result` defined. \n')
            runs.append(g['result'])
        except Exception as e:
            exceptions.append(
                f'\n### Exception on response {i}\n\n ```py \n{str(e)}\n```\n')
            runs.append(False)
    result = {'name': config['name'], 'context': context, 'result': runs}

    return result, '\n\n'.join(exceptions)  # + obj2html(context) Too long


def obj2html(o):
    # make new console with info
    reconfigure(record=True, file=open(os.devnull, 'w'))
    console = get_console()
    # with console.capture() as capture:
    console.print(inspect(o))
    info_html = console.export_html(inline_styles=True,
                                    code_format="<pre style=\"font-family: Menlo, 'DejaVu Sans Mono', consolas, 'Courier New', monospace\">{code}</pre>")
    return info_html
