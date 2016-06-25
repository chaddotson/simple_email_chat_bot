from distutils.core import setup
from os.path import dirname, join

version = '0.1.0'


def read(fname):
    return open(join(dirname(__file__), fname)).read()


with open("requirements.txt", "r") as f:
    install_reqs = map(str.strip, f.readlines())

setup(
    name='simple_email_chat_bot',
    version=version,
    packages=['bin'],
    url='',
    license='',
    author='Chad Dotson',
    author_email='chad@cdotson.com',
    description='',
    install_requires=install_reqs,
    dependency_links=["git+http://github.com/chaddotson/pytools.git#egg=pytools=0.1.1"],
    entry_points={
        'console_scripts': [
            'simple_email_chat_bot = bin.chatbot:main',
        ]
    },
)
