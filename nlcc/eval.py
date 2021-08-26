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
        print('Could not parse file')
        inspect(config, docs=False, methods=False)
        return None
    dir = os.path.dirname(path)
    with open(os.path.join(dir, config['prompt']), 'r') as f:
        query = f.read()
    # TODO Better way?
    # Make it so we can only get one function
    context.prompt.stop = ['def'] + context.prompt.stop
    context = nlp.code_completion(query, context, **kwargs)

    with open(os.path.join(dir, config['test']), 'r') as f:
        test_code = f.read()

    runs = []
    for r in context.responses:
        g = {}
        try:
            exec(r + '\n' + test_code, g)
            if 'result' not in g:
                print('Your eval code must have a variable called result')
            runs.append(g['result'])
        except Exception as e:
            runs.append(False)
    result = {'name': config['name'], 'context': context, 'result': runs}

    return result, obj2html(context)


def obj2html(o):
    # make new console with info
    reconfigure(record=True)
    console = get_console()
    # with console.capture() as capture:
    console.print(inspect(o))
    info_html = console.export_html(inline_styles=True,
                                    code_format="<pre style=\"font-family: Menlo, 'DejaVu Sans Mono', consolas, 'Courier New', monospace\">{code}</pre>")
    return info_html
