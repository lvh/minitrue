from setuptools import setup

setup(name='minitrue',
      version='0',
      description='',
      url='https://github.com/lvh/minitrue',

      author='Laurens Van Houtven',
      author_email='_@lvh.cc',

      packages=['minitrue'],

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