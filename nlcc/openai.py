import openai
import os
import time
from pyrate_limiter import Duration, Limiter, RequestRate

limiter = Limiter(RequestRate(23, Duration.MINUTE))


openai.api_key = os.getenv('OPENAI_API_KEY')


def code_engine(query, T=0.00, stop=None, n=1, max_tokens=896, language='python', engine="code-davinci-002"):
    suffix = None
    if '[insert]' in query:
        query, suffix = query.split('[insert]')
    if stop == []:
        stop = None
    while True:
        try:
            with limiter.ratelimit('codex', delay=True):
                response = openai.Completion.create(
                    engine=engine,
                    prompt=query,
                    temperature=T,
                    max_tokens=max_tokens,
                    top_p=1,
                    frequency_penalty=0.0,
                    presence_penalty=0,
                    stop=stop,
                    n=n,
                    suffix=suffix
                )
                break
        except openai.error.RateLimitError:
            time.sleep(15)
            continue
    if suffix is None:
        return [r['text'] for r in response['choices']]
    else:
        return [query + r['text'] + suffix for r in response['choices']]


def nlp_engine(query, T=0.3):
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
