## Toronto Planning Applications

This is a project of [Civic Tech Toronto](http://civictech.ca/) looking into [City of Toronto development project applications](http://app.toronto.ca/DevelopmentApplications/mapSearchSetup.do?action=init).

Revised to support for PostgreSQL with PostGIS added.

#### Usage

We're currently using Python ~2.7, with database options of MySQL and PostgreSQL.

To get the raw data for all wards:

`pip install requests`

`python scraper.py`

To parse that data and insert it into a database:

`pip install ppygis`

`conda install -c conda-forge pyproj`

`pip install pypostalcode`

`pip install geopy`

`pip install MySQL-python`

`conda install -c conda-forge psycopg2`

Create a mysql db using `schema_mysql.sql`, or create a postgresql db using `schema_pgsql.sql`.  Change the info in the `dbcfg-sample.py` for your installation and rename it to `dbcfg.py`.

`mysql -uUser -Ddbname < schema.sql`

Make sure you comment out the database type you want for parse.py. (Line 386 or 387)

`python parse.py`

Or run both those things together with

`python run.py`


