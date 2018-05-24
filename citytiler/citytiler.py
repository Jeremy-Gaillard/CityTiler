import yaml
import subprocess
import psycopg2
import argparse
from export import from_3dcitydb


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Convert CityGML files to 3D Tiles.')
    parser.add_argument('conf', help='path to configuration file')
    parser.add_argument('dbname', help='name of the database that stores or will be created to store the CityGML data')
    parser.add_argument('srs', nargs='?', help='SRID (e.g. 3946). Required with --files')
    parser.add_argument('srs_name', nargs='?', help='corresponding SRS name (e.g. crs:EPSG::3946). Required with --files')

    parser.add_argument('--files', nargs='*', help='list of CityGML files to convert. If no files are given, 3D Tiles files will be generated from the data already stored in the database')

    parser.add_argument('--dropdb', action='store_true', help='allows CityTiler to drop the database if it already exists at the beginning of the process')
    parser.add_argument('--append', action='store_true', help='add objects to an existing 3D City DB: do not create a new database, PostGIS extension and 3D City DB scheme')
    parser.add_argument('--output', default='.', help='output directory')

    args = parser.parse_args()

    if args.files is not None and args.append is False and (args.srs is None or args.srs_name is None):
        exit("srs and srs_name are required when the database has to be created")

    dbname = args.dbname

    configFile = open(args.conf, 'r')
    config = yaml.load(configFile)
    configFile.close()
    citydbJar = config['3DCITYDB_PATH'] + '/lib/3dcitydb-impexp.jar'
    citydbScripts = config['3DCITYDB_PATH'] + '/3dcitydb/postgresql'

    if args.files is not None and args.append is False:
        # Create DB
        completedProcess = subprocess.run(["createdb", dbname])
        if completedProcess.returncode != 0:
            if args.dropdb:
                subprocess.run(["dropdb", dbname])
                completedProcess = subprocess.run(["createdb", dbname])
                if completedProcess.returncode != 0:
                    exit()
            else:
                exit()



    db = psycopg2.connect(
        "postgresql://{0}:{1}@{2}:{3}/{4}"
        .format(config['PG_USER'], config['PG_PASSWORD'], config['PG_HOST'],
        config['PG_PORT'], dbname),
    )
    db.autocommit = True
    cursor = db.cursor()

    if args.files is not None and args.append is False:
        # Initialize DB
        cursor.execute('CREATE EXTENSION postgis');

        citydbConf = "/tmp/tmp_createdb.sh"
        outputConf = open(citydbConf, 'w')
        shellScript = """
        #!/bin/sh
        export PGPORT={0}
        export PGHOST={1}
        export PGUSER={2}
        export CITYDB={3}
        export PGBIN={4}
        export PGPASSWORD={5}

        # Run CREATE_DB.sql to create the 3D City Database instance
        "$PGBIN/psql" -d "$CITYDB" -f "/tmp/tmp_createdb.sql"
        """.format(config['PG_PORT'], config['PG_HOST'], config['PG_USER'], dbname, config['PG_PATH'], config['PG_PASSWORD'])
        outputConf.write(shellScript)
        outputConf.close()


        citydbConf = '/tmp/tmp_createdb.sql'
        inputConf = open(config['SQL_TEMPLATE'], 'r')
        outputConf = open(citydbConf, 'w')
        for s in inputConf.readlines():
            outputConf.write(s.replace('REPLACE_SRS_NO', args.srs).replace('REPLACE_GMLSRSNAME', args.srs_name))
        inputConf.close()
        outputConf.close()

        cl = 'cd ' + citydbScripts + ' && sh /tmp/tmp_createdb.sh'
        print(cl)
        subprocess.run(cl, shell=True)

    if args.files is not None:
        # Configure 3D CityDB using temporary file
        citydbConf = '/tmp/tmp_citydbconf.xml'
        inputConf = open(config['3DCITYDB_CONFIG_TEMPLATE'], 'r')
        outputConf = open(citydbConf, 'w')
        for s in inputConf.readlines():
            outputConf.write(s.replace('POSTGIS_HOST', config['PG_HOST']).replace('POSTGIS_PORT', config['PG_PORT']).replace('POSTGIS_DATABASE_NAME', dbname).replace('POSTGIS_USER_NAME', config['PG_USER']).replace('POSTGIS_PASSWORD', config['PG_PASSWORD']))
        inputConf.close()
        outputConf.close()

        cl = '{0} -jar "{1}" -shell -import {2} -config "{3}"'.format(config['JAVA_CL'], citydbJar, ';'.join(['"{0}"'.format(f) for f in args.files]), citydbConf)
        print(cl)
        subprocess.run(cl, shell=True)

        # We need to reconnect to the database after modifying it with another process for some reason
        db.close()
        db = psycopg2.connect(
            "postgresql://{0}:{1}@{2}:{3}/{4}"
            .format(config['PG_USER'], config['PG_PASSWORD'], config['PG_HOST'],
            config['PG_PORT'], dbname),
        )
        db.autocommit = True
        cursor = db.cursor()

    # Create 3D Tiles
    from_3dcitydb(cursor, args.output)
