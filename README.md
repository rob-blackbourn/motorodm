# motorodm
A python object document mapper for MongoDB using the asyncio motor package

# Installation

Install directly from git with:

```bash
pip install git+git://github.com/rob-blackbourn/motorodm
```

or

```bash
pip install https+git://github.com/rob-blackbourn/motorodm
```

Testing
-------

The project uses pytest, so the usual pytest commands work:

```bash
(venv) ~/motorodm$ pip install -r requirements_dev.txt
(venv) ~/motorodm$ pytest
```

Some markers have been setup
- unit
- integration
- regression

So to run all unit test the following would work:

```bash
(venv) ~/motorodm$ pytest -v -m unit
```

The test framework has been integrated with setup.py, so the following also works
```bash
(venv) ~/motorodm$ python setup.py test
(venv) ~/motorodm$ python setup.py test --addopts '-v -m unit'

There is a docker compose file which will create an environment suitable for integration tests.
This assumes mongo is not already running locally (as it uses the default port) and requires docker and docker-compose.

