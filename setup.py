from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
   name='paramount',
   version='0.0.2',
   description='Automated accuracy measurements for LLMs',
   long_description=long_description,
   long_description_content_type='text/markdown',
   author='Hakim K',
   author_email='5586611+hakimkhalafi@users.noreply.github.com',
   url='https://github.com/ask-fini/paramount',
   project_urls={
      'Source Code': 'https://github.com/ask-fini/paramount'
   },
   packages=find_packages(),
   install_requires=[]
)
