import os
import openai
from dataclasses import dataclass

openai.api_key = os.getenv('OPENAI_API_KEY')

prompts = {
    'mdtraj': '''import mdtraj as md'''
}


@dataclass
class Context:
    type: str = ''
    prompt: str = ''


def _query_codex(query, training_string, T=0.00):
    prompt = '\n'.join([training_string, '"""\n' + query, '\n"""\n'])
    # return prompt
    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=prompt,
        temperature=T,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0,
        stop=['"""']
    )
    return response['choices'][0]['text'], response

def _query_gpt3(query):
    # return prompt
    response = openai.Completion.create(
    engine="davinci",
    prompt=f"This takes text and identifies which computational chemistry library it is about.\n\nText: \"Let's do something with mdtraj\"\nLibrary: mdtraj\n###\nText: \"MD in gromacs\"\nLibrary: gromacs\n###\nText: \"Protein analysis\"\nLibrary: mdtraj\n###\nText: \"Write a slurm script\"\nLibrary: slurm\n###\nText: \"{query}\"\nLibrary:",
    temperature=0.3,
    max_tokens=60,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    stop=["###"]
    )

    return response['choices'][0]['text'], response

import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")



def run_gpt_search(query, context, auto_context=False):
    if context is None:
        r,full_response = _query_gpt3(query)
        r = r.split()[0]
        if r in prompts:
            context = Context(r, prompts[r])
        else:
            if auto_context is True:
                context = Context(r, f'# This script is for the {r} library')
            else:
                context = Context('','')
    else:
        r, _ = _query_codex(query, context.prompt)
    result = r
    return result, context
