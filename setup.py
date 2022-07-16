#!/usr/bin/env python3

from setuptools import setup

setup(
    name='git-branch-selector',
    version='0.1.1',
    description='Select a git branch using arrow keys.',
    license='BSD',
    author='ytyng',
    author_email='ytyng@live.jp',
    url='https://github.com/ytyng/git-branch-selector.git',
    keywords='CUI, Git, branch, selector, arrow, keyboard, command',
    packages=['git_branch_selector'],
    entry_points={
        'console_scripts': [
            'git-branch-selector = '
            'git_branch_selector.git_branch_selector:main',
        ]
    },
)
