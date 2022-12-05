from transformers import AutoTokenizer, AutoModelForCausalLM


_models = {}
_tokenizers = {}

def code_engine(query, T=0.00, stop=None, n=1, max_tokens=896,
                model=None, language='python',
                max_retries=100):
    if '[insert]' in query:
        raise NotImplementedError('cannot insert in general HF')
    if model is None:
        raise ValueError('must specify model')
    if model not in _models:
        _tokenizers[model] = AutoTokenizer.from_pretrained(model)
        _models[model] = AutoModelForCausalLM.from_pretrained(model)
    result = None
    input_ids = _tokenizers[model](query, return_tensors="pt").input_ids
    generated_ids = _models[model].generate(input_ids, max_length=min(250, max_tokens), temperature=max(0.01, T),
                                   num_return_sequences=n, top_p=0.95, do_sample=True)

    result = [_tokenizers[model].decode(generated_ids[i], skip_special_tokens=True) for i in range(n)]
    return [query + r for r in result]


def nlp_engine(query, model='gpt2', min_length=50, T=-1):
    return None
