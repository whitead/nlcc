import os
from glob import glob
from setuptools import setup

exec(open('nlcc/version.py').read())

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name='nlcc',
      version=__version__,
      description='Natural language computational chemistry',
      author='Andrew & Frank',
      author_email='andrew.white@rochester.edu',
      url='https://github.com/whitead/nlcc',
      license='MIT',
      packages=['nlcc'],
      install_requires=[
          'click', 'importlib_resources',
          'importlib-metadata',
          'numpy', 'pyyaml',
          'openai', 'pyperclip',
          'prompt_toolkit', 'tabulate', 'pyrate-limiter',
          'rich'],
      test_suite='tests',
      zip_safe=True,
      entry_points='''
        [console_scripts]
        nlcc=nlcc.main:main
        nlcc-eval=nlcc.main:eval
        nlcc-bench=nlcc.main:benchmark
        nlcc-prompts=nlcc.main:prompts
        nlcc-human=nlcc.main:human_check
            ''',
      package_data={'nlcc': ['prompts/*yml']},
      long_description=long_description,
      long_description_content_type="text/markdown",
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Topic :: Scientific/Engineering :: Bio-Informatics",
          "Topic :: Scientific/Engineering :: Chemistry",
          "Topic :: Scientific/Engineering :: Artificial Intelligence"
      ]
      )
