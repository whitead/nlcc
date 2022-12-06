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
    language: str = 'python'
    emoji: str = '💻'


@dataclass
class Context:
    name: str = ''
    prompt: Prompt = None
    text: str = ''
    T: float = 0.0
    responses: tuple = None
    query_type: str = None


# load prompts on import
prompts = {}

for f in files(nlcc.prompts).iterdir():
    c = yaml.safe_load(f.read_text())
    for k, v in c.items():
        prompts.update({k: Prompt(**v)})


def guess_query_type(query):
    if '[insert]' in query:
        return 'insert'
    if len(query) == 0:
        return 'continue'
    if len(query.split('\n')) == 1:
        return 'comment'
    return 'code'


def code_completion(query, context, engine, query_type=None, T=0.0, n=1, def_end=False):
    context.T = T
    if len(context.text) == 0:
        context.text = context.prompt.text
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
            query if len(context.text) > 0 else query
    elif query_type == 'code' or query_type == 'insert':
        query = context.text + '\n' + \
            query if len(context.text) > 0 else query
    context.query = query
    context.query_type = query_type
    r = engine(query, T=T, stop=context.prompt.stop + (['def'] if def_end else []),
               n=n, language=context.prompt.language)
    context.responses = tuple(
        [ri if query_type == 'insert' else query + ri for ri in r])
    return context


def guess_context(query, engine, T=0.4):
    # check for exact match
    matched = None
    for p in prompts:
        if query.lower() == p.lower():
            matched = p
            e = prompts[p].emoji
    # try engine match
    if not matched and len(query.strip()) > 0:
        r, _ = engine(query, T=T)
        if r is not None:
            r = r.split()[0]
            e, r = r.split(',')
            if r in prompts:
                matched = r
    if matched:
        context = Context(e + ' ' + matched,
                          prompts[matched], prompts[matched].text)
    else:
        context = Context(e, Prompt())
    return context
