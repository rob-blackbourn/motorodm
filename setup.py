import ast
import codecs
import os
import sys
from setuptools import setup, find_packages


PY_VER = sys.version_info
PACKAGE_NAME = 'motorodm'

if not PY_VER >= (3, 5):
    raise RuntimeError("motorodm doesn't support Python earlier than 3.5")


def read(f):
    with codecs.open(os.path.join(os.path.dirname(__file__), f),
                     encoding='utf-8') as ofile:
        return ofile.read()


class VersionFinder(ast.NodeVisitor):
    def __init__(self):
        self.version = None

    def visit_Assign(self, node):
        if not self.version:
            if node.targets[0].id == '__version__':
                self.version = node.value.s


def read_version():
    init_py = os.path.join(os.path.dirname(__file__),
                           PACKAGE_NAME, '__init__.py')
    finder = VersionFinder()
    finder.visit(ast.parse(read(init_py)))
    if finder.version is None:
        msg = f'Cannot find version in {PACKAGE_NAME}/__init__.py'
        raise RuntimeError(msg)
    return finder.version


install_requires = ['motor>=2.0.0', 'graphene>=2.1.3']

setup(name=PACKAGE_NAME,
      version=read_version(),
      description=("An ODM for motor."),
      lond_description=read('README.md'),
      classifiers=[
          'License :: OSI Approved :: Apache Software License',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Framework :: AsyncIO',
      ],
      author="Rob Blackbourn",
      author_email="rob.blackbourn@gmail.com",
      url='https://github.com/rob-blackbourn/motorodm/',
      license='Apache 2',
      packages=find_packages(),
      install_requires=install_requires,
      include_package_data=True)
