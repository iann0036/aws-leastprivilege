#!/usr/bin/env python
import sys
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

version = sys.version_info[:2]
if version < (3, 4):
    print('cfnlp requires Python version 3.4 or later' +
          ' ({}.{} detected).'.format(*version))
    sys.exit(-1)

setup(name='cfnlp',
      version='0.1.1',
      description='Generates an IAM policy for the CloudFormation service role that adheres to least privilege',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Ian Mckay',
      author_email='cfnlp@ian.mn',
      url='https://github.com/iann0036/cfn-leastprivilege',
      license='MIT',
      packages=find_packages(exclude=['tests', 'tests.*']),
      zip_safe=True,
      install_requires=[
          'boto3>=1.10.41'
          'cfn_flip>=1.2.2'
      ],
      entry_points={'console_scripts': [
          'cfnlp = cfnlp.main:main'
      ]}
)
