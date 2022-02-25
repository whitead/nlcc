import nlcc
import yaml
import os


def test_context_match():
    c = nlcc.nlp.guess_context('bash', None)
    assert c.prompt == nlcc.nlp.prompts['bash']
    completion = nlcc.nlp.code_completion(
        'echo', c, nlcc.openai.code_engine, n=3)
