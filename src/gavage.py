#!/usr/bin/env python
# vim: set expandtab:

"""

License: GPL V2 See LICENSE file
Author: Jim Richardson
email: weaselkeeper@gmail.com

gavage stuffs data it is handed, into a mongo collection.

"""
PROJECTNAME = 'distaff'
import os
import sys
from ConfigParser import SafeConfigParser
import logging
try:
    from pymongo import Connection
except ImportError as e:
    print 'Failed import of pymmongo, system says %s' % e
    sys.exit(1)


# Basic logging setup
logging.basicConfig(level=logging.WARN,
                    format='%(asctime)s %(levelname)s - %(message)s',
                    datefmt='%y.%m.%d %H:%M:%S')

# Setup logging to console by default

console = logging.StreamHandler(sys.stderr)
console.setLevel(logging.WARN)
logging.getLogger(PROJECTNAME).addHandler(console)
log = logging.getLogger(PROJECTNAME)

### Set some default variables and constants.
config = os.path.join('/etc', PROJECTNAME, PROJECTNAME + '.conf')


def connectDB(_args):
    """ Open a connection to the mongodb, need the host, the collection name,
    and the dbname """
    host = _args.mongodb_host
    log.debug("connecting to mongo db host %s", host)
    database = _args.dbname
    log.debug("connecting to db %s", database)
    collection = _args.collection
    log.debug("Using collection name %s", collection)
    con = Connection(host)
    col = con[database][collection]
    log.debug('selecting database/collection: %s/%s',
              database, collection)
    return col


def update(collection, host):
    """ host is a dict, containing free form info, only required entry is
    host:hostname, of course, that's pretty useless, so more data in the same
    key:value syntax would be useful"""

    log.debug('In update')
    log.debug('in collection %s working on host %s', collection, host)
    log.debug('exiting update')


def run(_args, CONFIGFILE):
    """ Now parse the config file.  Get any and all info from config file."""
    log.debug('in Run, with %s and %s', _args, CONFIGFILE)
    configparse = SafeConfigParser()
    if os.path.isfile(CONFIGFILE):
        _config = CONFIGFILE
    else:
        log.warn('No config file found at %s', CONFIGFILE)
        sys.exit(1)
    configparse.read(_config)
    if _args.mongohost:
        mongohost = _args.mongohost
        log.warn('mongohost is %s', mongohost)
    else:
        mongohost = configparse.get('gavage', 'mongohost')
    log.warn('Using host %s for mongodb', mongohost)

    db = configparse.get('gavage', 'dbname')
    collection = configparse.get('gavage', 'collection')
    user = configparse.get('gavage', 'user')
    passwd = configparse.get('gavage', 'passwd')
    print db, collection, user, passwd


def update(collection, newhostdata, host):
    """ updating info for host """
    log.debug('in update')

    cursor = collection.find({'_id': host })

    collection.update(
            {'_id': host},
            {'$set': {
                newhostdata
                    }
                },upsert=True
            )
    return

# Here we start if called directly (the usual case.)
if __name__ == "__main__":
    # This is where we will begin when called from CLI. No need for argparse
    # unless being called interactively, so import it here
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
    parser.add_argument('-m', '--mongohost', action='store',
        help='Host that holds the mongodb collections')

    args = parser.parse_args()
    args.usage = PROJECTNAME + ".py [options]"

    if args.debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.WARN)

    if args.config:
        config = args.config

    sys.exit(run(args, config))
