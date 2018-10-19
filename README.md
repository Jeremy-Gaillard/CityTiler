CityTiler is a tool to convert CityGML files to 3D Tiles.

# Features

- Export untextured Lod2 buildings in the 3D Tiles format
- The semantic hierarchical organisation of the buildings is preserved: each building part is individually accessible
- **Warning : not all ways of storing LoD2 geometries are supported at the time being. Your mileage may vary**

# Installation

CityTiler requires the installation of the following tools:
- [3DCityDB 3.3.2](https://www.3dcitydb.org/)
- [PostgreSQL](https://www.postgresql.org/) and [PostGIS](http://postgis.net/)
- [Python 3](https://www.python.org/)

```bash
$ virtualenv -p /usr/bin/python3 venv
$ . venv/bin/activate
(venv)$ pip install -e .
```

CityTiler uses a version of py3dtiles that has not yet been published. You will need to install it manually.

```bash
$ git clone https://github.com/jeremy-gaillard/py3dtiles/
$ cd py3dtiles
$ git checkout bt_hierarchy
# Move back to CityTiler directory
$ pip install path/to/py3dtiles --upgrade
```

# Configuration

Open conf/config.yml and fill in the undefined fields.

# Usage

The full documentation of the different parameters is available via the command line interface:

```bash
(venv)$ python citytiler/citytiler.py -h
```

Here are a few examples of how you can use the exporter. The CityGML file used in these examples is available on the [Grand Lyon open data website](https://data.grandlyon.com/localisation/maquette-3d-texturfe-de-la-commune-de-villeurbanne-mftropole-de-lyon/).

If you want to export a CityGML file without having to create and populate the database yourself:

```bash
(venv)$ python citytiler/citytiler.py conf/config.yml citytiler 3946 crs:EPSG::3946 --files 'VILLEURBANNE_2015/VILLEURBANNE_BATI_2015.gml' --output './tilesets'
```

If you want to export the content of a database that uses the 3D City DB scheme:

```bash
(venv)$ python citytiler/citytiler.py conf/config.yml citytiler --output './tilesets'
```

If you want to add new data to a database that uses the 3D City DB scheme and export it :

```bash
(venv)$ python citytiler/citytiler.py conf/config.yml citytiler --files 'VILLEURBANNE_2015/VILLEURBANNE_BATI_2015.gml' --output './tilesets' --append
```
