# Copyright (c) 2008-2015 by Enthought, Inc.
# All rights reserved.

import os
import re
import subprocess
from setuptools import setup, find_packages

MAJOR = 4
MINOR = 6
MICRO = 0

IS_RELEASED = True

VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)


# Return the git revision as a string
def git_version():
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for k in ['SYSTEMROOT', 'PATH']:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        out = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, env=env,
        ).communicate()[0]
        return out

    try:
        out = _minimal_ext_cmd(['git', 'describe', '--tags'])
    except OSError:
        out = ''

    git_description = out.strip().decode('ascii')
    expr = r'.*?\-(?P<count>\d+)-g(?P<hash>[a-fA-F0-9]+)'
    match = re.match(expr, git_description)
    if match is None:
        git_revision, git_count = 'Unknown', '0'
    else:
        git_revision, git_count = match.group('hash'), match.group('count')

    return git_revision, git_count


def write_version_py(filename='apptools/_version.py'):
    template = """\
# THIS FILE IS GENERATED FROM APPTOOLS SETUP.PY
version = '{version}'
full_version = '{full_version}'
git_revision = '{git_revision}'
is_released = {is_released}

if not is_released:
    version = full_version
"""
    # Adding the git rev number needs to be done inside
    # write_version_py(), otherwise the import of apptools._version messes
    # up the build under Python 3.
    fullversion = VERSION
    if os.path.exists('.git'):
        git_rev, dev_num = git_version()
    elif os.path.exists('apptools/_version.py'):
        # must be a source distribution, use existing version file
        try:
            from apptools._version import git_revision as git_rev
            from apptools._version import full_version as full_v
        except ImportError:
            raise ImportError("Unable to import git_revision. Try removing "
                              "apptools/_version.py and the build directory "
                              "before building.")

        match = re.match(r'.*?\.dev(?P<dev_num>\d+)', full_v)
        if match is None:
            dev_num = '0'
        else:
            dev_num = match.group('dev_num')
    else:
        git_rev = 'Unknown'
        dev_num = '0'

    if not IS_RELEASED:
        fullversion += '.dev{0}'.format(dev_num)
    else:
      fullversion += '+ansys.ch'

    with open(filename, "wt") as fp:
        fp.write(template.format(version=VERSION,
                                 full_version=fullversion,
                                 git_revision=git_rev,
                                 is_released=IS_RELEASED))

if __name__ == "__main__":
    write_version_py()
    from apptools import __version__, __requires__

    setup(name='apptools',
          version=__version__,
          author='Enthought, Inc.',
          author_email='info@enthought.com',
          maintainer='ETS Developers',
          maintainer_email='enthought-dev@enthought.com',
          url='https://docs.enthought.com/apptools',
          download_url=('https://www.github.com/enthought/apptools'),
          classifiers=[c.strip() for c in """\
                Development Status :: 5 - Production/Stable
                Intended Audience :: Developers
                Intended Audience :: Science/Research
                License :: OSI Approved :: BSD License
                Operating System :: MacOS
                Operating System :: Microsoft :: Windows
                Operating System :: OS Independent
                Operating System :: POSIX
                Operating System :: Unix
                Programming Language :: Python
                Topic :: Scientific/Engineering
                Topic :: Software Development
                Topic :: Software Development :: Libraries
              """.splitlines() if len(c.strip()) > 0],
          description='application tools',
          long_description=open('README.rst').read(),
          long_description_content_type="text/x-rst",
          include_package_data=True,
          package_data={'apptools': ['help/help_plugin/*.ini',
                                     'help/help_plugin/action/images/*.png',
                                     'logger/plugin/*.ini',
                                     'logger/plugin/view/images/*.png',
                                     'naming/ui/images/*.png',
                                     'preferences/tests/*.ini'
                                     ]
                        },
          install_requires=__requires__,
          license='BSD',
          packages=find_packages(),
          platforms=["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
          zip_safe=False,
          )
