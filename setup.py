# Ultralytics MkDocs plugin

from setuptools import setup, find_packages
from pathlib import Path

setup(
    name='mkdocs-ultralytics-plugin',
    version='0.0.21',
    description='An MkDocs plugin that provides Ultralytics Docs customizations at https://docs.ultralytics.com.',
    long_description=Path('README.md').read_text(encoding='utf-8'),
    long_description_content_type='text/markdown',
    author='Ultralytics',
    author_email='hello@ultralytics.com',
    url='https://github.com/ultralytics/ultralytics',
    project_urls={
        'Bug Reports': 'https://github.com/ultralytics/mkdocs/issues',
        'Funding': 'https://ultralytics.com',
        'Source': 'https://github.com/ultralytics/mkdocs'},
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
