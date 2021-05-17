#!/usr/bin/env python

import setuptools
from distutils.core import setup

setup(name="turbofloat",
      version="4.4.4.1",
      description="Python integration for the LimeLM TurboFloat library. This lets you add floating licensing (a.k.a. concurrent licensing) to your Python app.",
      url="https://wyday.com/limelm/help/using-turbofloat-with-python/",
      download_url="https://github.com/wyday/python-turbofloat",
      author="wyDay, LLC",
      author_email="support@wyday.com",
      maintainer="wyDay, LLC",
      maintainer_email="support@wyday.com",
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Topic :: Software Development :: Libraries :: Python Modules',
		  'Programming Language :: Python',
		  'Programming Language :: Python :: 2',
		  'Programming Language :: Python :: 3',
      ],
      packages=["turbofloat"],
      long_description=open("README.md").read(),
      long_description_content_type="text/markdown"
)
