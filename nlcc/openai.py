import openai
import os

openai.api_key = os.getenv('OPENAI_API_KEY')


def code_engine(query, T=0.00, stop=None, n=1):
    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=query,
        temperature=T,
        max_tokens=64,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0,
        stop=stop,
        n=n,
    )
    if n==1:
        return response['choices'][0]['text']
    else:
        return response


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
