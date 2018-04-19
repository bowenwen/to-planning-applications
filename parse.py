import re
import os
import dbcfg
import MySQLdb
import sys
import traceback

# postgresql and spatial packages
import psycopg2
import ppygis  # Point
import pyproj  # Proj, transform

# postal code location processing
import pypostalcode # PostalCodeDatabase
import geopy #from geopy.geocoders import Nominatim

import time
import json

TABLENAME = "to_planning_app"  #"parse"
DATA_DIR = 'data'
DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), DATA_DIR)
FILENAME_LOG_FILE = 'message.log'
FILENAME_LOG_INVALID_DATAROWS = 'bad_rows.log'
DATA_LOG_INVALID_DATAROWS = ''

#####################
# UTILITY FUNCTIONS #
#####################

# geopy geocoder
def do_geocode(address):
    geolocator = geopy.geocoders.Nominatim()
    try:
        return geolocator.geocode(address)
    except geopy.exc.GeocoderTimedOut:
        time.sleep(10)
        return do_geocode(address)


##################################
# PUTTING DATA INTO DICTIONARIES #
##################################


# entry point
def build_all_objects():
    # parallelize loops with joblib: https://blog.dominodatalab.com/simple-parallelization/
    all_objects = []
    for dirpath, _, filenames in os.walk(DATA_PATH):
        for f in filenames:
            file = os.path.join(dirpath, f)
            big_list = string_to_list(file)
            try:
                keys = get_main_record_keys(big_list[-2])
            except ValueError:
                print f + " doesn't contain valid records."
                pass
            big_list = clean(big_list)
            pointer_map = build_pointer_map(keys, big_list)

            ward_results = build_objects(keys, big_list, pointer_map)

            # add the ward queried to get this result to the actual data
            ward_int = int(f[1:-2])
            # add if statement for 0-'COMMUNITY_PLANNING',1-'ADJUSTMENT_COMMITTEE',2-'LOCAL_APPEAL'
            apptyp_int = int(f[-1:])
            apptyp_string = ''
            if apptyp_int == 0:
                apptyp_string = 'COMMUNITY_PLANNING'
            elif apptyp_int == 1:
                apptyp_string = 'ADJUSTMENT_COMMITTEE'
            elif apptyp_int == 2:
                apptyp_string = 'LOCAL_APPEAL'

            for development in ward_results:
                ward_results[development]["ward_queried"] = ward_int
                ward_results[development]["app_typ"] = apptyp_string

            # add to the all_objects array
            all_objects.append(ward_results)
    return all_objects


def string_to_list(file):
    return open(file).read().split(";")


def is_key(s):
    return re.search('s\d+', s)


def get_main_record_keys(s):
    '''Return a list of all the "outer keys", found at the end of the data files'''
    return s[s.index('[') + 1:-2].split(',')


def clean(big_list):
    return map(str.strip,
               big_list)[:-2]  # we don't need the last two items in the file


def build_pointer_map(keys, big_list):
    '''
  Here we're looking for entries where the values are pointers, i.e. s0.proposal=s33
  Return a dict that takes the form {key : [pointer, name]} i.e. {'s0' : ['s33','proposal' ]}
  '''
    pointer_map = {}
    for item in big_list:
        try:
            key_name, pointer = item.split('=')
            key, name = key_name.split('.')
            if is_key(key) and is_key(pointer):
                pointer_map[pointer] = [key, name]
        except ValueError:
            pass
    return pointer_map


def build_objects(keys, big_list, pointer_map):
    '''
  Main processing function for each data file that contains developments for a single ward.
  Return a dictionary of dictionaries, where each inner dictionary contains the information
  for a single development.  Development data can be 'nested' within the data files. Currently
  this goes one nesting level deep when creating development objects.

  big_list is a list of all the key-value pairs that comes straight from the data files.  each
  element of the list is actually a string at this point that gets split below...
  '''
    obj = {}
    for key in keys:
        obj[key] = {}
    for item in big_list:

        # we get a ValueError if strings aren't of the form sNUM.key = STRING
        # but that's okay because we want to ignore those values
        try:
            key_name, value = item.split('=')
            key, value_name = key_name.split('.', 1)
            value = value.replace('"', '')  # remove unneeded quote marks

            # now we have key, value_name and value

            # skip over the entries that are just pointers, we have those in pointer_map
            if not is_key(value):

                # check if the key is an 'outer key'
                if key in obj.keys():
                    obj[key][value_name] = value

                # this is a pointer
                elif key in pointer_map.keys():
                    outer_key = pointer_map[key][0]

                    # even though pointers are nested, for now we only go one level deep
                    if outer_key in obj.keys():
                        value_name = pointer_map[key][1] + "_" + value_name
                        obj[outer_key][value_name] = value

        except ValueError:
            pass

    return obj


#########################
# CONVENIENCE FUNCTIONS #
#########################


def print_objects(objects):
    for key in objects:
        print key
        for k, v in objects[key].iteritems():
            print k + ": " + v
        print


def get_sorted_value_names(objects):
    s = set()
    for k, v in objects.iteritems():
        for name in v.keys():
            s.add(name)
    s = list(s)
    s.sort()
    return s


################
# DB FUNCTIONS #
################


# MySQLdb variant
# run schema_mysql.sql in mysql when running script for the first time
def mysql_connect():
    return MySQLdb.connect(
        host=dbcfg.mysql['host'],
        user=dbcfg.mysql['user'],
        passwd=dbcfg.mysql['passwd'],
        db=dbcfg.mysql['db'])


def mysql_add_row(cursor, tablename, rowdict):
    keys = ", ".join(rowdict.keys())
    values_template = ", ".join(["%s"] * len(rowdict))

    keys_and_values_template_for_update = ', '.join(
        '%s=%s' % z for z in zip(rowdict.keys(), ["%s"] * len(rowdict)))

    sql = ('INSERT INTO %s (%s) VALUES (%s) '
           'ON DUPLICATE KEY '
           'UPDATE %s') % (tablename, keys, values_template,
                           keys_and_values_template_for_update)

    values = tuple(rowdict[key] for key in rowdict)
    cursor.execute(sql, values * 2)


# PostgreSQL variant
# run schema_postgres.sql in postgreSQL when running script for the first time
def pgsql_connect():
    return psycopg2.connect(
        host=dbcfg.mysql['host'],
        user=dbcfg.mysql['user'],
        password=dbcfg.mysql['passwd'],
        dbname=dbcfg.mysql['db'])


def pgsql_add_row(cursor, tablename, rowdict, includegeom):
    
    global DATA_LOG_INVALID_DATAROWS

    keys = ", ".join(rowdict.keys())
    values_template = ", ".join(["%s"] * len(rowdict))

    if (includegeom):
        values_template = values_template + ", %s"
        # create list of shapely geometries while projecting project existing coordinate to WGS84
        sql = ("""INSERT INTO %s (%s, geom) VALUES (%s) """) % (
            tablename, keys, values_template)
        values = tuple(rowdict[key] for key in rowdict)

        # prevent reference error, check if keys exist, if not, create None entries
        if not 'propX' in rowdict.keys():
            rowdict['propX'] = None
        if not 'propY' in rowdict.keys():   
            rowdict['propY'] = None         
        if not 'location' in rowdict.keys():
            rowdict['location'] = None
        if not 'propertyView_postal' in rowdict.keys():
            rowdict['propertyView_postal'] = None
        if not 'propertyView_city' in rowdict.keys():
            rowdict['propertyView_city'] = None
        if not 'propertyView_province' in rowdict.keys():
            rowdict['propertyView_province'] = 'ON' # assume this for this dataset
            
        # if contains proX and proY, use that to build geom
        # elif contains address, use that to estimate geom (more accurate but slower, with sleep to prevent IP block)
        # elif contains postal code, use that to estimate geom (less accurate but faster)
        # else there isn't enough geographical information, exclude this row
        if rowdict['propX'] is not None and rowdict['propY'] is not None:            
            inProj = pyproj.Proj(
                init='epsg:2019'
            )  #SRID_MTM3 for city of toronto # http://spatialreference.org/ref/epsg/2019/
            outProj = pyproj.Proj(init='epsg:4326')  #SRID_WGS84
            x1, y1 = rowdict['propX'], rowdict['propY']
            x2, y2 = pyproj.transform(inProj, outProj, x1, y1)
        elif rowdict['location'] is not None:
            address = "%s, %s, %s" % (rowdict['location'], rowdict['propertyView_city'], rowdict['propertyView_province'])
            location = do_geocode(address) # recursive retry method to get address
            if location is not None:
                x2, y2 = (location.longitude, location.latitude) # https://postgis.net/2013/08/18/tip_lon_lat/
            else:
                badrowstring = json.dumps(rowdict)
                DATA_LOG_INVALID_DATAROWS = DATA_LOG_INVALID_DATAROWS + badrowstring + '\n'
                return # continue to next row
            time.sleep(5) #sleep to prevent server block
        elif rowdict['propertyView_postal'] is not None:
            # Compute x2, y2 from postal code instead
            # https://github.com/inkjet/pypostalcode
            pcdb = pypostalcode.PostalCodeDatabase()
            pc = rowdict['propertyView_postal']#postal
            location = pcdb[pc]
            x2, y2 = (location.longitude,location.latitude)
        else:
            badrowstring = json.dumps(rowdict)
            DATA_LOG_INVALID_DATAROWS = DATA_LOG_INVALID_DATAROWS + badrowstring + '\n'
            return # continue to next row

        # insert into database
        coordinate = ppygis.Point(x2, y2)  # longitude, latitude
        coordinate.srid = 4326  #SRID_WGS84
        values_withgeom = values + (coordinate, )
        try:
            cursor.execute(sql, values_withgeom)
        except psycopg2.DataError as de1:
            a=1

    else:
        sql = ('INSERT INTO %s (%s) VALUES (%s) ') % (tablename, keys,
                                                      values_template)
        values = tuple(rowdict[key] for key in rowdict)
        cursor.execute(sql, values)

##################
# DATA CLEANSING #
##################


def null_empty_str_to_none(val):
    return None if val == "null" or val == '' else val


# very hacky for now, we don't want folder fields to be converted to ints
def try_int_conversion(key, val):
    if key.startswith("folder"):
        return val
    else:
        try:
            int_val = int(val.replace(',', ''))
            return int_val
        except (ValueError, AttributeError):
            return val


########
# MAIN #
########


def run(db_typ='postgres', include_geom=True):
    """
    Run Parser

    """
    print('parsing...')
    all_objects = build_all_objects()

    db = pgsql_connect() if db_typ == 'postgres' else mysql_connect()
    cursor = db.cursor()
    tablename = TABLENAME

    new_count = 0
    duplicate_count = 0

    print('inserting into db...')
    for ward_object in all_objects:
        for development in ward_object.keys():
            row = ward_object[development]
            row = {k: null_empty_str_to_none(v) for k, v in row.iteritems()}
            row = {k: try_int_conversion(k, v) for k, v in row.iteritems()}
            new_count+=1
            if db_typ == 'postgres':
                try:
                    pgsql_add_row(cursor, tablename, row, include_geom)
                except psycopg2.IntegrityError:
                    #print("duplicate value.")#(e1.message)
                    new_count-=1
                    duplicate_count+=1
                    db.rollback()
            else:
                try:
                    mysql_add_row(cursor, tablename, row)
                #except MySQLdb.IntegrityError:
                    # new_count-=1
                    # duplicate_count+=1
                except:
                    e = sys.exc_info()[0]
                    print e
                    traceback.print_exc()
                    print row
                    sys.exit(0)

    print("Summary:\nDuplicate Records: %s\nNew Records: %s" % (str(duplicate_count),str(new_count)))
    db.commit()


if __name__ == "__main__":
    import sys
    old_stdout = sys.stdout
    log_file = open(FILENAME_LOG_FILE,"w")
    sys.stdout = log_file # logging to file starts here, with print

    # run statement
    run(db_typ='postgres', include_geom=True)
    # run(db_typ='mysql', include_geom=True)
    
    sys.stdout = old_stdout
    bad_row_file = open(FILENAME_LOG_INVALID_DATAROWS,"w")
    bad_row_file.write(DATA_LOG_INVALID_DATAROWS)
    bad_row_file.close()

    log_file.close()
