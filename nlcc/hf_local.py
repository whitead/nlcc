from transformers import AutoTokenizer, AutoModelForCausalLM
import torch


_models = {}
_tokenizers = {}


def code_engine(query, T=0.00, stop=None, n=1, max_tokens=250,
                engine=None, language='python',
                max_retries=100):
    model = engine
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    if '[insert]' in query:
        raise NotImplementedError('cannot insert in general HF')
    if model is None:
        raise ValueError('must specify model')
    if model not in _models:
        _tokenizers[model] = AutoTokenizer.from_pretrained(model)
        _models[model] = AutoModelForCausalLM.from_pretrained(model).to(device)
    result = None
    input_ids = _tokenizers[model](
        query, return_tensors="pt").to(device).input_ids
    generated_ids = _models[model].generate(input_ids, max_length=max_tokens, temperature=max(0.01, T),
                                            num_return_sequences=n, top_p=0.95, do_sample=True)

    result = [_tokenizers[model].decode(
        generated_ids[i], skip_special_tokens=True) for i in range(n)]
    # remove query
    result = [r.replace(query, '') for r in result]
    # apply stop tokens
    for i, r in enumerate(result):
        if stop is not None:
            for s in stop:
                if s in r:
                    result[i] = r[:r.index(s)]
    return result


def nlp_engine(query, model='gpt2', min_length=50, T=-1):
    return None
