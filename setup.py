import logging
import sys

from setuptools import setup, find_packages
from logging import StreamHandler

# _log = logging.getLogger("sasclient")
# _log.setLevel(logging.DEBUG)
# _handler = StreamHandler(sys.stderr)
# _handler.setLevel(logging.DEBUG)
# _log.addHandler(_handler)

setup(
    name='metaswitchsasclient',
    version='0.1',
    packages=find_packages('src'),
    package_dir={'':'src'},
    # test_suite='metaswitch.sasclient.test',
    install_requires=[],
    # tests_require=[]
    )
