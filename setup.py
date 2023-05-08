# Ultralytics MkDocs plugin
# Usage:
# pip install mkdocs-ultralytics-plugin
# plugins:
#   - mkdocstrings
#   - search
#   - ultralytics

from setuptools import setup, find_packages
from pathlib import Path

setup(
    name='mkdocs-ultralytics-plugin',
    version='0.0.9',
    description='An MkDocs plugin that generates meta description and image tags based on the first paragraph and the '
                'first image in a page',
    long_description=Path('README.md').read_text(encoding='utf-8'),
    author='Ultralytics',
    author_email='hello@ultralytics.com',
    license='AGPL-3.0',
    packages=find_packages(),
    install_requires=[
        'mkdocs>=1.0',
        'beautifulsoup4>=4.9.3',
    ],
    entry_points={
        'mkdocs.plugins': [
            'ultralytics = plugin:MetaPlugin'
        ]
    }
)
