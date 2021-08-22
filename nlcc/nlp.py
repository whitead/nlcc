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


openai.api_key = os.getenv('OPENAI_API_KEY')


prompts = {}

for f in files(nlcc.prompts).iterdir():
    c = yaml.safe_load(f.read_text())
    for k, v in c.items():
        prompts.update({k: Prompt(**v)})


def _query_codex(query, T=0.00, stop=None):
    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=query,
        temperature=T,
        max_tokens=64,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0,
        stop=stop
    )
    return response['choices'][0]['text']


def _query_gpt3(query, T=0.3):
    response = openai.Completion.create(
        engine="davinci",
        prompt=f"This takes text and identifies which computational chemistry library it is about and gives an appropriate emoji. \n\nText: \"Let's do something with mdtraj\"\nLibrary: ⚗,mdtraj\n###\nText: \"MD in gromacs\"\nLibrary: 🍏,gromacs\n###\nText: \"Protein analysis\"\nLibrary: 🌳,biopython\n###\nText: \"Write a slurm script\"\nLibrary: 📝,slurm\n###\nText: \"{query}\"\nLibrary:",
        temperature=T,
        max_tokens=60,
        top_p=1,
        best_of=3,
        frequency_penalty=0,
        presence_penalty=0,
        stop=["###"]
    )

    return response['choices'][0]['text'], response


openai.api_key = os.getenv("OPENAI_API_KEY")


def run_gpt_search(query, context, codex_temp=0.0, gpt3_temp=0.3):
    if context is None:
        r, full_response = _query_gpt3(query, T=gpt3_temp)
        r = r.split()[0]
        e, r = r.split(',')
        print(e, r)
        if r in prompts:
            context = Context(e + ' ' + r, prompts[r], prompts[r].text)
        else:
            context = Context(e, Prompt())
    else:
        # count newlines to guess if we should insert comments (and how)
        if len(query) > 0:
            if len(query.split('\n')) == 1:
                if context.prompt.multiline_comment:
                    query = context.prompt.multiline_comment + '\n' + \
                        query + '\n' + context.prompt.multiline_comment + '\n'
                else:
                    query = context.prompt.comment + ' ' + query + '\n'
            query = context.text + '\n' + \
                query if len(context.text) > 0 else query
        else:
            query = context.text + query
        r = _query_codex(query, T=codex_temp, stop=context.prompt.stop)
        context.text = query + r
    result = r
    return result, context
