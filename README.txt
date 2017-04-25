csc
===============================

Getting Started
---------------

- remove old python environment
deactivate
conda remove -y -n csc --all

- remove old project
cd \workspace
rmdir /s /q csc

- create python environment
c:
cd \workspace
conda config -y --add channels conda-forge
conda create -y -n csc pyramid pip
activate csc
pip install pony bcrypt
conda install -y cookiecutter

- create project
c:
cd \workspace
activate csc
cookiecutter https://github.com/Pylons/pyramid-cookiecutter-starter
y
csc
csc
1
cd csc

- run test
pip install -e ".[testing]"
pytest

- run server
pserve development.ini


- add mixins to editor result
(\w*)\((.*)\):
$1($2, csc.model_mixins.$1Mixin):