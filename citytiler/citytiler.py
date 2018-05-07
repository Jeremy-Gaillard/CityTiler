import yaml
import subprocess
import psycopg2
from export import from_3dcitydb

TMP_config = 'conf/config.yml'
TMP_cityGML = ['/media/data/Backup villes/VILLEURBANNE_2015/VILLEURBANNE_BATI_2015.gml']
TMP_dbname = 'tilertest'
TMP_SRS_NO = '3946'
TMP_GML_SRS_NAME = 'crs:EPSG::3946'

if __name__ == '__main__':

    configFile = open(TMP_config, 'r')
    config = yaml.load(configFile)
    configFile.close()
    citydbJar = config['3DCITYDB_PATH'] + '/lib/3dcitydb-impexp.jar'
    citydbScripts = config['3DCITYDB_PATH'] + '/3dcitydb/postgresql'

    # TEMP
    db = psycopg2.connect(
        "postgresql://{0}:{1}@{2}:{3}/{4}"
        .format(config['PG_USER'], config['PG_PASSWORD'], config['PG_HOST'],
        config['PG_PORT'], TMP_dbname),
    )
    db.autocommit = True
    cursor = db.cursor()
    from_3dcitydb(cursor)
    exit()
    # END TEMP

    # Initialize DB
    cl = 'createdb ' + TMP_dbname
    print(cl)
    subprocess.run(cl.split())

    db = psycopg2.connect(
        "postgresql://{0}:{1}@{2}:{3}/{4}"
        .format(config['PG_USER'], config['PG_PASSWORD'], config['PG_HOST'],
        config['PG_PORT'], TMP_dbname),
    )
    db.autocommit = True
    cursor = db.cursor()

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
    """.format(config['PG_PORT'], config['PG_HOST'], config['PG_USER'], TMP_dbname, config['PG_PATH'], config['PG_PASSWORD'])
    outputConf.write(shellScript)
    outputConf.close()


    citydbConf = '/tmp/tmp_createdb.sql'
    inputConf = open(config['SQL_TEMPLATE'], 'r')
    outputConf = open(citydbConf, 'w')
    for s in inputConf.readlines():
        outputConf.write(s.replace('REPLACE_SRS_NO', TMP_SRS_NO).replace('REPLACE_GMLSRSNAME', TMP_GML_SRS_NAME))
    inputConf.close()
    outputConf.close()

    cl = 'cd ' + citydbScripts + ' && sh /tmp/tmp_createdb.sh'
    print(cl)
    subprocess.run(cl, shell=True)


    # Configure 3D CityDB using temporary file
    citydbConf = '/tmp/tmp_citydbconf.xml'
    inputConf = open(config['3DCITYDB_CONFIG_TEMPLATE'], 'r')
    outputConf = open(citydbConf, 'w')
    for s in inputConf.readlines():
        outputConf.write(s.replace('POSTGIS_HOST', config['PG_HOST']).replace('POSTGIS_PORT', config['PG_PORT']).replace('POSTGIS_DATABASE_NAME', TMP_dbname).replace('POSTGIS_USER_NAME', config['PG_USER']).replace('POSTGIS_PASSWORD', config['PG_PASSWORD']))
    inputConf.close()
    outputConf.close()

    cl = '{0} -jar "{1}" -shell -import {2} -config "{3}"'.format(config['JAVA_CL'], citydbJar, ';'.join(['"{0}"'.format(f) for f in TMP_cityGML]), citydbConf)
    print(cl)
    subprocess.run(cl, shell=True)

    # Create 3D Tiles
    from_3dcitydb(cursor)
