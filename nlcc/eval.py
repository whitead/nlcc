import yaml
from . import nlp
import os
from rich import inspect


def eval_single(path, **kwargs):
    with open(path, 'r') as f:
        config = yaml.safe_load(f.read())
    try:
        context = nlp.Context(name=config['name'], prompt=nlp.prompts[config['context']])
    except Exception as e:
        print('Could not parse file')
        inspect(config, docs=False, methods=False)
        return None
    dir = os.path.dirname(path)
    with open(os.path.join(dir, config['prompt']), 'r') as f:
        query = f.read()
    context = nlp.code_completion(query, context, **kwargs)

    with open(os.path.join(dir, config['test']), 'r') as f:
        test_code = f.read()

    runs = []
    for r in context.responses:
        g = {}
        exec(r + '\n' + test_code, g)
        if 'result' not in g:
            print('Your eval code must have a variable called result')
        runs.append(g['result'])
    result = {'name': config['name'], 'context': context, 'result': runs}
    return result