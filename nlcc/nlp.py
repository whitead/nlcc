import nlcc.prompts
import os
import openai
import unicodedata
from dataclasses import dataclass
from importlib_resources import files
import yaml


@dataclass
class Prompt:
    text: str = ''
    comment: str = '# '
    multiline_comment: str = None
    stop: list = None


@dataclass
class Context:
    name: str = ''
    prompt: Prompt = None
    text: str = ''
    T: float = 0.0


# load prompts on import
prompts = {}

for f in files(nlcc.prompts).iterdir():
    c = yaml.safe_load(f.read_text())
    for k, v in c.items():
        prompts.update({k: Prompt(**v)})


def guess_query_type(query):
    if len(query) == 0:
        return 'continue'
    if len(query.split('\n')) == 1:
        return 'comment'
    return 'code'


def code_completion(query, context, engine, query_type=None, T=0.0, n=1):
    # count newlines to guess if we should insert comments (and how)
    if query_type is None:
        query_type = guess_query_type(query)
    if query_type == 'continue':
        query = context.text + query
    elif query_type == 'comment':
        if context.prompt.multiline_comment:
            query = context.prompt.multiline_comment + '\n' + \
                query + '\n' + context.prompt.multiline_comment + '\n'
        else:
            query = context.prompt.comment + ' ' + query + '\n'
        query = context.text + '\n' + \
            query if context is not None and len(context.text) > 0 else query
    elif query_type == 'code':
        query = context.text + '\n' + \
            query if context is not None and len(context.text) > 0 else query
    r = engine(query, T=T, stop=context.prompt.stop, n=n)
    context.text = query + r[0]
    return context, r

def guess_context(query, engine, T=0.3):
    r, _ = engine(query, T=T)
    r = r.split()[0]
    e, r = r.split(',')
    if r in prompts:
        context = Context(e + ' ' + r, prompts[r], prompts[r].text)
    else:
        context = Context(e, Prompt())
    return context
