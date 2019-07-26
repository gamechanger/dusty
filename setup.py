# ## GAMECHANGER_CI_PREVENT_BUILD
import sys
from setuptools import find_packages


def read(path):
    with open(path, 'rb') as fid:
        return fid.read().decode('utf-8')


try:
    from restricted_pkg import setup
except ImportError:
    # allow falling back to setuptools only if
    # we are not trying to upload
    if 'upload' in sys.argv:
        raise ImportError('restricted_pkg is required to upload, first do pip install restricted_pkg')
    from setuptools import setup


setup(
    name='dusty',
    version='0.0.1',
    description='Docker-based development environment manager',
    url='https://github.com/gamechanger/dusty',
    private_repository='gamechanger',
    author='GameChanger',
    packages=find_packages(),
    package_data={'dusty': ['resources/*']},
    install_requires=read('requirements.txt').splitlines(),
    tests_require=read('requirements-dev.txt').splitlines()[1:],
    test_suite="nose.collector",
    entry_points={'console_scripts':
                  ['dusty = dusty.cli.__init__:main']},
    zip_safe=False
)
