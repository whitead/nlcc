from .eval import sanitize
from .nlp import code_completion, prompts, Context
from .main import get_engine

def run(prompt, context, engine='openai'):
    _, code_engine = get_engine(engine)
    if isinstance(context, str):
        p = prompts[context]
        context = Context(
            name=context, prompt=p)
    # make config for eval_single
    result = code_completion(prompt, context, code_engine)
    code = sanitize(result.responses[0])
    return code