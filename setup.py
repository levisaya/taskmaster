from distutils.core import setup

setup(
    name='taskmaster',
    version='0.1',
    packages=['taskmaster'],
    url='',
    license='MIT',
    author='Andy Levisay',
    author_email='levisaya@gmail.com',
    description='Server to manage and monitor long running processes.',
    install_requires=["django>=1.7",
                      "six>=1.8.0",
                      "psutil>=2.1.3",
                      "tornado>=4.0"]
)
