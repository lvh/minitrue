from setuptools import find_packages, setup

setup(name='minitrue',
      version='0',
      description='Proxy designed to lie.',
      url='https://github.com/lvh/minitrue',

      author='Laurens Van Houtven',
      author_email='_@lvh.cc',

      packages=find_packages(),

      install_requires=['twisted'],

      license='ISC',
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Twisted",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Topic :: Internet :: Proxy Servers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Security",
        ])