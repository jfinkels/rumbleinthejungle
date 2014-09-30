"""
rumbleinthejungle
=================

rumbleinthejungle prints humorous rhyming phrases of the form "the dispute in
Beirut", as appears in the 2009 film `*The Slammin' Salmon*
<http://www.imdb.com/title/tt1135525/>`_, itself an homage to the historic
boxing match entitled `The Rumble in the Jungle
<https://en.wikipedia.org/wiki/The_Rumble_in_the_Jungle>`_.

For more information on this package, see
  * `PyPI listing <http://pypi.python.org/pypi/rumbleinthejungle>`_
  * `Source code repository <http://github.com/jfinkels/rumbleinthejungle>`_

"""
from setuptools import setup
from setuptools.command.install import install as _install
import sys


class install(_install):
    """Installs the necessary NLTK data after the installation of this package
    has completed.

    """
    def run(self):
        """Installs the CMU pronunciation dictionary data from NLTK by running
        the command-line NLTK downloader.

        """
        import subprocess
        super().run()
        try:
            subprocess.call(['python', '-m', 'nltk.downloader', 'cmudict'])
        except OSError:
            print('Failed to download CMU pronunciation dictionary data.')
            print('Maybe try running:')
            print('  python -c "import nltk; nltk.download()".')
            sys.exit(-1)

setup(
    author='Jeffrey Finkelstein',
    author_email='jeffrey.finkelstein@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Games/Entertainment'
    ],
    cmdclass={'install': install},
    description='A command-line program that prints rhyming phrases.',
    download_url='http://pypi.python.org/pypi/rumbleinthejungle',
    install_requires=['nltk'],
    include_package_data=True,
    license='GNU GPLv3+',
    long_description=__doc__,
    name='rumbleinthejungle',
    platforms='any',
    test_suite='nose.collector',
    tests_require=['nose'],
    url='http://github.com/jfinkels/rumbleinthejungle',
    version='0.0.1',
    # zip_safe=False
)
