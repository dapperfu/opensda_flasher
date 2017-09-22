"""Python Setup File."""
from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='opensda_flasher',
      version='0.1',
      description='Tool to flash DEVKIT-MPC57xx devices with OpenSDA.',
      url='https://github.com/jed-frey/opensda_flasher',
      author='Jedediah Frey',
      author_email='opensda_flasher@exstatic.org',
      license='BSD',
      zip_safe=False,
      packages=['opensda_flasher'],
      package_data={'opensda_flasher': ['opensda_flasher/opensda_flasher.ini']},
      install_requires=requirements,
      entry_points={
          'console_scripts': ['osf = opensda_flasher.cli:main',
                              'opensda_flasher = opensda_flasher.cli:main'],
      })
