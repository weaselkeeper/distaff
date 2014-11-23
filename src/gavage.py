#!/usr/bin/env python
# vim: set expandtab:
###
# Copyright (c) 2013, Jim Richardson <weaselkeeper@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###



"""

License: GPL V2 See LICENSE file
Author: Jim Richardson
email: weaselkeeper@gmail.com

gavage stuffs data it is handed, into a mongo collection.

"""
PROJECTNAME = 'distaff'
import os
import sys
import ConfigParser
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
    try:
        col = con[database][collection]
    except:
        log.info('Failed to open connection to %s', database)
    log.debug('selecting database/collection: %s/%s',
              database, collection)
    return col


def run(_args, CONFIGFILE):
    """ Now parse the config file.  Get any and all info from config file."""
    log.debug('in Run, with %s and %s', _args, CONFIGFILE)
    configparse = ConfigParser.SafeConfigParser()
    if os.path.isfile(CONFIGFILE):
        _config = CONFIGFILE
    else:
        log.warn('No config file found at %s', CONFIGFILE)
        sys.exit(1)
    configparse.read(_config)
    if _args.mongohost:
        _args.mongohost = _args.mongohost
    else:
        _args.mongohost = configparse.get('gavage', 'mongohost')
    log.debug('using host %s for mongodb', _args.mongohost)

    _args.dbname = configparse.get('gavage', 'dbname')

    _args.collection = configparse.get('gavage', 'collection')
    _args.user = configparse.get('gavage', 'user')
    _args.passwd = configparse.get('gavage', 'passwd')
    log.debug(_args)
    col = connectDB
    log.debug("leaving run")

def update(col, newhostdata, host):
    """ updating info for host """
    log.debug('in update')

    cursor = col.find({'_id': host})

    col.update(
        {'_id': host},
        {'$set': {newhostdata}}, upsert=True)
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
