import os
import openai


def code_engine(query, T=0.00, stop=None):
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


def nlp_engine(query,model='EleutherAI/gpt-neo-2.7B', min_length=50, T=-1):
    import json
    import requests

    API_TOKEN = os.getenv('HUGGINGFACE_API_KEY')
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    API_URL = f"https://api-inference.huggingface.co/models/{model}"
    prompt=f"This takes text and identifies which computational chemistry library it is about and gives an appropriate emoji. \n\nText: \"Let's do something with mdtraj\"\nLibrary: ⚗,mdtraj\n###\nText: \"MD in gromacs\"\nLibrary: 🍏,gromacs\n###\nText: \"Protein analysis\"\nLibrary: 🌳,biopython\n###\nText: \"Write a slurm script\"\nLibrary: 📝,slurm\n###\nText: \"{query}\"\nLibrary:"
    prompt = prompt + " [MASK]"
    prompt = {"inputs": prompt}

    data = json.dumps(prompt)
    web_response = requests.request("POST", API_URL, headers=headers, data=data)
    response = json.loads(web_response.content.decode("utf-8"))
    print(response)
    prompt_and_response = response[0]['generated_text']
    print(prompt)
    print(prompt_and_response)
    only_response = prompt_and_response.split(prompt)[1]
    print(only_response)

    return only_response,response
