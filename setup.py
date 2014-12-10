from setuptools import setup
import sys


python_2_dependencies = []

if sys.version_info < (3,):
    python_2_dependencies.append('importlib>=1.0.3')

setup(
    name='taskmaster',
    version='0.1',
    packages=['taskmaster'],
    url='',
    license='MIT',
    author='Andy Levisay',
    author_email='levisaya@gmail.com',
    description='Server to manage and monitor long running processes.',
    install_requires=["psutil>=2.1.3",
                      "tornado>=4.0",
                      "mako>=1.0.0"]
)
