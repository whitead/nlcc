import os
import requests
import json
import time
import re
from pyrate_limiter import Duration, Limiter, RequestRate

API_TOKEN = os.getenv('HUGGINGFACE_API_KEY')

limiter = Limiter(RequestRate(15, Duration.MINUTE))

# lots of code from https://github.com/dpfried/incoder/blob/main/example_usage.py

# signals the start of a document
BOS = "<|endoftext|>"
# signals the end of a generated infill
EOM = "<|endofmask|>"


def make_sentinel(i):
    # signals (1) a location to insert an infill and (2) the start of the infill generation
    if i is None:
        return ''
    return f"<|mask:{i}|>"


def strip_metadata(s):
    # grab it if it contains new line
    s = re.sub(r'\<|.+\>|\n\{0,1\}', '', s)
    # possible end of line
    s = re.sub(r'\<|.+$', '', s)
    return s


def code_engine(query, T=0.00, stop=None, n=1, max_tokens=896,
                model='facebook/incoder-1B', language='python',
                max_retries=100):
    suffix = None
    base_query = query
    if '[insert]' in query:
        query, suffix = query.split('[insert]')
        # encode parts separated by sentinel
        enc_query = query + make_sentinel(0)
        enc_query += suffix
        enc_query += make_sentinel(1)
        base_query = enc_query

    if language == 'python':
        base_query = '<| file ext=.py |>\n' + base_query

    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    API_URL = f"https://api-inference.huggingface.co/models/{model}"
    result = None
    for _ in range(max_retries):
        enc_query = base_query
        try:
            if suffix:
                enc_query += make_sentinel(0)
            data = dict(inputs=enc_query,
                        options=dict(use_gpu=True, use_cache=True,
                                     wait_for_model=False),
                        parameters=dict(return_full_text=False, max_new_tokens=min(250, max_tokens),  # ??
                                        temperature=max(0.01, T), num_return_sequences=n, top_p=0.95, do_sample=True,
                                        prefix=BOS))
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
                stop_index = -1
                for s in stop + [EOM]:
                    if s in completion:
                        stop_index = completion.index(s)
                        break
                completion = completion[:stop_index]
                completion = strip_metadata(completion)
                result.append(completion)
            break
        except:
            # probably a timeout or 503
            time.sleep(15)
            continue
    if result is None:
        raise ValueError('Tried too many times')
    if suffix is None:
        return result
    else:
        return [query + r + suffix for r in result]


def nlp_engine(query, model='gpt2', min_length=50, T=-1):
    return None
