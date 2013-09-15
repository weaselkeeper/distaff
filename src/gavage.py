#!/usr/bin/env python
# vim: set expandtab:

"""

License: GPL V2 See LICENSE file
Author: Jim Richardson
email: weaselkeeper@gmail.com

gavage stuffs data it is handed, into a mongo collection.

"""
PROJECTNAME='distaff'
import os
import sys
from ConfigParser import SafeConfigParser
import logging
try:
    from pymongo import Connection
except ImportError as e:
    print 'Failed import of pymmongo, system says %s' % e
    sys.exit(1)


def run():

    logging.basicConfig(level=logging.WARN,
                        format='%(asctime)s %(levelname)s - %(message)s',
                        datefmt='%y.%m.%d %H:%M:%S')

    # Setup logging to console by default

    console = logging.StreamHandler(sys.stderr)
    console.setLevel(logging.WARN)
    logging.getLogger(PROJECTNAME).addHandler(console)
    log = logging.getLogger(PROJECTNAME)

    ### Set some default variables and constants.
    CONFIGFILE = os.path.join('/etc', PROJECTNAME,PROJECTNAME +'.conf')
    return log, CONFIGFILE


def connectDB(args):
    """ Open a connection to the mongodb, need the host, the collection name,
    and the dbname """
    host = args.mongodb_host
    log.debug("connecting to mongo db host %s" % host)
    database = args.dbname
    log.debug("connecting to db %s" % database)
    collection = args.collection
    log.debug("Using collection name %s" % collection)
    try:
        con = Connection(host)
        col = con[database][collecion]
        log.debug('selecting database/collection: %s/%s' % (database, collection))
    except:
        log.warn("Something went wrong with connecting to %s on %" % (collection,host))
    return col

def update(collection, host):
    """ host is a dict, containing free form info, only required entry is
    host:hostname """
    log.debug('In update')
    #Blah blah blah, some mongodb stuff here, needs more thinking FIXME



def get_config(args,CONFIGFILE):
    # Now parse the config file.  Get any and all info from config file.
    parser = SafeConfigParser()
    configuration = {}
    if os.path.isfile(CONFIGFILE):
        config = CONFIGFILE
    else:
        log.warn('No config file found at %s' % CONFIGFILE)
        sys.exit(1)
    try:
        if args.mongodbhost:
            mongodb_host = args.mongodbhost
        else:
            mongodb_host = parser.get('mongodb_host','host')
    except:
        log.warn('config parse failed')
        sys.exit(1)
    log.warn('Using %s for mongodb' % mongodb_host)
    parser.read(config)
    return parser


# Here we start if called directly (the usual case.)
if __name__ == "__main__":
    """This is where we will begin when called from CLI. No need for argparse
    unless being called interactively, so import it here"""
    log, config = run()
    import argparse

    parser = argparse.ArgumentParser(
        description='Someproject does something')
    parser.add_argument('-n', '--dryrun', action='store_true',
        help='Dry run, do not actually perform action', default=False)
    parser.add_argument('-d', '--debug', action='store_true',
        help='Enable debugging during execution.', default=None)
    parser.add_argument('-r', '--readable', action='store_true', default=False,
        help='Display output in human readable formant (as opposed to json).')
    parser.add_argument('-c', '--config', action='store', default=None,
        help='Specify a path to an alternate config file')
    parser.add_argument('-m','--mongodbhost', action='store',
        help='Host that holds the mongodb collections')

    args = parser.parse_args()
    args.usage = PROJECTNAME + ".py [options]"


    if args.debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.WARN)
    if args.config:
        CONFIGFILE = args.config

    _parse_config = get_config(args,CONFIGFILE)
