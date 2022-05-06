import json
import os

import requests

API_TOKEN = os.getenv('HUGGINGFACE_API_KEY')
print(API_TOKEN)
API_URL = "https://api-inference.huggingface.co/models/gpt2"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

#data = query("Can you please let us know more details about your ")
#print(data)

API_URL = "https://api-inference.huggingface.co/models/mrm8488/CodeGPT-small-finetuned-python-token-completion"
#API_URL = "https://api-inference.huggingface.co/models/EleutherAI/gpt-neo-2.7B"
def query(payload):
    data = json.dumps(payload)
    response = requests.request("POST", API_URL, headers=headers, data=data)
    return json.loads(response.content.decode("utf-8"))

data = query(
    {
        "inputs": {
            "comment": "# This is a python function which averages an array x\n\n",
            "context": "We are generaing python code.",
        },
        "parameters": {
            "min_length": 50,
        }
    }
)

print(data)
