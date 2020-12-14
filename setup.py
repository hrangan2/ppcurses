#!/usr/bin/env python

from distutils.core import setup

setup(name='ppcurses',
      url='https://github.com/hrangan2/ppcurses',
      version='0.2',
      description='An ncurses interface to Projectplace',
      long_description='An ncurses interface to Projectplace',
      author='Harshavardhan Rangan',
      author_email='hrangan@planview.com',
      packages=['ppcurses'],
      entry_points={
          'console_scripts': [
              'ppcurses = ppcurses.main:main',
             ],
            },
      include_package_data=True,
      install_requires=[
          'requests',
          'python-dateutil',
          ],
      classifiers=[
          'Environment :: Console :: Curses',
          'Development Status :: 3 - Alpha',
          ]
      )
