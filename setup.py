from distutils.core import setup

setup(
    name='PyLogger',
    version='0.1.0',
    author='Gabe Ochoa',
    author_email='gabe@wink.com',
    packages=['pylogger', 'pylogger.test'],
    url='https://github.com/winkapp/pylogger',
    description='a python logging library',
    long_description=open('README.txt').read()
)
