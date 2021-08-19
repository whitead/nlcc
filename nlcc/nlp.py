import os
import openai

openai.api_key = os.getenv('OPENAI_API_KEY')

_mdtraj_prompt = '''
import mdtraj as md
'''


def _query_gpt3(query, training_string, T=0.00):
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


def run_gpt_search(query):
    result = {'type': 'mdtraj Command'}
    r, _ = _query_gpt3(query, _mdtraj_prompt)
    result['data'] = r
    return result
