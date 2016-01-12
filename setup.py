from setuptools import setup

setup(name='Langsim',
      version='1.0',
      packages=["langsim"],
      package_dir={'langsim': 'src/langsim'},
      package_data={'langsim': ['src/langsim/data/walsdata/language.csv']},
      description='Language Similarity Tools for Python',
      author='Stephen Mayhew',
      author_email='swm.mayhew@gmail.com',
      url='www.stephen-mayhew.com/langsim',
      include_package_data=True,
      )