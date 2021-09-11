# Backend of SAY App and Panel

[![Build, Test and Deploy](https://github.com/SAY-DAO/backend/actions/workflows/pipeline.yml/badge.svg)](https://github.com/SAY-DAO/backend/actions/workflows/pipeline.yml)

Setting up Development Environment on Linux

----------------------------------
### Installing Dependencies

    $ sudo apt-get install libass-dev libpq-dev postgresql \
        build-essential redis-server redis-tools

### Setup Python environment

- Make sure you have `python3.8`

```bash
sudo pip3 install virtualenvwrapper
echo "export VIRTUALENVWRAPPER_PYTHON=`which python3.8`" >> ~/.bashrc
echo "alias v.activate=\"source $(which virtualenvwrapper.sh)\"" >> ~/.bashrc
source ~/.bashrc
v.activate
mkvirtualenv --python=$(which python3.8) --no-site-packages say_backend
```
    
#### Activating virtual environment
    
```bash
workon say_backend
```

### Installing dependencies

```bash
pip install -r requirements.txt
```

### Run Local Server

    ./scripts/dev-run.sh
