import sys
from setuptools import setup, setuptools

__author__ = 'Iván de Paz Centeno'


if sys.version_info < (3, 4, 1):
    sys.exit('Python < 3.4.1 is not supported!')


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='proxyup',
      version="0.0.1",
      description='Proxy updater',
      long_description=readme(),
      long_description_content_type='text/markdown',
      url='',
      author='Iván de Paz Centeno',
      author_email='ipazc@unileon.es',
      packages=setuptools.find_packages(),
      install_requires=[
          "requests", "pandas"
      ],
      classifiers=[
          'Development Status :: 1 - Planning',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Education',
          'Natural Language :: English',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
      ],
      entry_points = {
          'console_scripts': ['cur=curdump.entry_point:main'],
      },
      test_suite='nose.collector',
      tests_require=['nose'],
      include_package_data=True,
      keywords="proxy api check list free",
      zip_safe=False)