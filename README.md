# BONSAI Seeder

`bseeder` is a CLI utility that parses `.ttl` files and updates their content to the Jena instance on https://db.bonsai.uno/ .

```bash
bseeder -h
```

**Setup:** To run it requires a `config.ini` file, see the example file `config.ini.sample`

```
python setup.py install
```

## With docker

```
docker build  . -t bonsai/bseeder -f bseeder.dockerfile

docker run -it --rm bonsai/bseeder -h


docker run -it --rm -v "$PWD/config.ini":/config.ini -v "$PWD/data":/data bonsai/bseeder -i /data/*.ttl
```

## TODO

Basic project description

Badges in Markdown format:

* For readthedocs, click on the info button next to the badge in https://readthedocs.org/projects/whatever/, and copy the markdown code
* For travis, click on the badge in https://travis-ci.org/BONSAMURAIS/whatever, and copy the markdown code
* For appveyor, go to the projects settings page, and then click on "badges", and copy the markdown code

## Installation

Details on how to install the package

```
pipenv install

pipenv shell
```

## Contributing

Details on how to contribute
