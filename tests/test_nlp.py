import nlcc
import yaml
import os


def test_context_match():
    c = nlcc.nlp.guess_context('bash', None)
    assert c.prompt == nlcc.nlp.prompts['bash']
