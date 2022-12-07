import os
import requests
import json
import time
import re
from pyrate_limiter import Duration, Limiter, RequestRate

API_TOKEN = os.getenv('HUGGINGFACE_API_KEY')

limiter = Limiter(RequestRate(15, Duration.MINUTE))


def code_engine(query, T=0.00, stop=None, n=1, max_tokens=896,
                engine=None, language='python',
                max_retries=100):
    if '[insert]' in query:
        raise NotImplementedError('cannot insert in general HF')
    if engine is None:
        raise ValueError('must specify model/engine')
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    API_URL = f"https://api-inference.huggingface.co/models/{engine}"
    result = None
    for _ in range(max_retries):
        try:
            data = dict(inputs=query,
                        options=dict(use_gpu=True, use_cache=False,
                                     wait_for_model=False),
                        parameters=dict(return_full_text=False, max_new_tokens=min(250, max_tokens),  # ??
                                        temperature=max(0.01, T), num_return_sequences=n, top_p=0.95, do_sample=True))
            with limiter.ratelimit('hugging', delay=True):
                web_response = requests.request(
                    "POST", API_URL, headers=headers, data=json.dumps(data))
            response = json.loads(web_response.content.decode("utf-8"))
            if 'estimated_time' in response:
                time.sleep(int(response['estimated_time']))
                continue
            if 'timed out' in response:
                time.sleep(15)
                continue
            result = []
            for r in response:
                if 'generated_text' not in r:
                    raise ValueError(
                        'No generated_text in response: ' + json.dumps(response))
                completion = r['generated_text']
                if query in completion:
                    completion = completion.replace(query, '')
                result.append(completion)
            break
        except requests.exceptions.ConnectionError:
            # probably a timeout or 503
            time.sleep(15)
            continue
    if result is None:
        raise ValueError('Tried too many times')
    # apply stop tokens
    for i, r in enumerate(result):
        if stop is not None:
            for s in stop:
                if s in r:
                    result[i] = r[:r.index(s)]
    return result


def nlp_engine(query, model='gpt2', min_length=50, T=-1):
    return None
