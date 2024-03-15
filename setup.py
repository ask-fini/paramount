from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
   name='paramount',
   version='0.2.4',
   description='Business Evals for LLMs',
   long_description=long_description,
   long_description_content_type='text/markdown',
   entry_points={
       'console_scripts': ['paramount=paramount.server.cli:main'],
   },
   author='Hakim K',
   author_email='5586611+hakimkhalafi@users.noreply.github.com',
   url='https://github.com/ask-fini/paramount',
   project_urls={
      'Source Code': 'https://github.com/ask-fini/paramount'
   },
   packages=find_packages(),
   install_requires=['pandas', 'pytz', 'flask', 'python-dotenv', 'scikit-learn', 'sqlalchemy', 'psycopg2-binary', 'gunicorn', 'toml']
)
