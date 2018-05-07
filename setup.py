from setuptools import setup

setup(name='citytiler',
      version='0.1',
      description='Convert CityGML to 3D Tiles',
      url='http://TO.DO',
      author='Jérémy Gaillard',
      author_email='jeremy.c.gaillard.pro@gmail.com',
      license='TODO',
      packages=['citytiler'],
      install_requires=[
          'py3dtiles',
          'pyyaml',
      ],
      zip_safe=False)
