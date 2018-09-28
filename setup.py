from distutils.core import setup

setup(
    name='PyLogger',
    version='0.1.0',
    author='Gabe Ochoa',
    author_email='gabe@wink.com',
    packages=['py_logger', 'py_logger.test'],
    url='https://github.com/winkapp/pylogger',
    description='A python logging library',
    long_description=open('README.md').read()
)
