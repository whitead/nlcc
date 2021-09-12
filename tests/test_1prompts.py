import os
import yaml


def test_prompt_validity():
    for root, dirs, files in os.walk(os.getcwd()):
        for filename in files:
            if filename.endswith(".yml"):
                path = os.path.join(root, filename)
                try:
                    with open(path, 'r') as f:
                        yaml.load(f)
                except yaml.YAMLError as exc:
                    print('Failed in', path)
                    print(exc)
