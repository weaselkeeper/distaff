#!/usr/bin/env python
# vim: set expandtab:
###
# Copyright (c) 2012, Jim Richardson <weaselkeeper@gmail.com>
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

"""
PROJECTNAME = 'distaff'
import os
import sys
import ConfigParser
import logging
import re
import urllib

try:
    from bs4 import BeautifulSoup as BS
except ImportError:
    print """ Please ensure availablility of python-bs4 module """

# Setup logging
logging.basicConfig(level=logging.WARN,
                    format='%(asctime)s %(levelname)s - %(message)s',
                    datefmt='%y.%m.%d %H:%M:%S')

# Setup logging to console.
console = logging.StreamHandler(sys.stderr)
console.setLevel(logging.WARN)
logging.getLogger(PROJECTNAME).addHandler(console)
LOG = logging.getLogger(PROJECTNAME)


def run(_args):
    """ Do, whatever it is, we do. """
    LOG.debug('in run function')
    # parse config
    parsed_config = get_config(_args)
    _url = parsed_config['SOURCEURL']
    query = parsed_config['QUERY']
    result = urllib.urlopen(_url).read()

    LOG.debug((_args, parsed_config))
    get_hostnames(result, query)
    LOG.debug('leaving run')
    return


def get_hostnames(data, query):
    """ Extract the hostnames """
    LOG.debug('in get_hostnames extracting hostnames from datastream')
    soup = BS(data)
    table = soup.find("table", attrs={"class": "table table-striped"})
    print query
    for row in table.find_all(href=re.compile(query)):
        print row.contents[0]
    LOG.debug('leaving get_hostnames')


def get_options():
    """ Parse the command line options"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Scrapes a URL for a host listing, pretty specific')
    parser.add_argument('-n', '--dry-run', action='store_true',
                        help='Dry run, do not actually perform action',
                        default=False)
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable debugging during execution.',
                        default=None)
    parser.add_argument('-r', '--readable', action='store_true', default=False,
                        help='Display output in human readable formant.')
    parser.add_argument('-c', '--config', action='store', default=None,
                        help='Specify a path to an alternate config file')
    parser.add_argument('-s', '--srcurl', action='store', dest='SOURCEURL',
                        help='bogus option for explanations')
    parser.add_argument('-q', '--query', action='store', dest='QUERY',
                        help='bogus option for explanations')

    _args = parser.parse_args()
    _args.usage = PROJECTNAME + ".py [options]"

    return _args


def get_config(_args):
    """ Now parse the config file.  Get any and all info from config file."""
    LOG.debug('Now in get_config')
    parser = ConfigParser.SafeConfigParser()
    configuration = {}
    configfile = os.path.join('/etc', PROJECTNAME, PROJECTNAME + '.conf')
    if _args.config:
        _config = _args.config
    else:
        if os.path.isfile(configfile):
            _config = configfile
        else:
            LOG.warn('No config file found at %s', configfile)
            sys.exit(1)

    parser.read(_config)

    if _args.SOURCEURL:
        configuration['SOURCEURL'] = _args.SOURCEURL
    else:
        configuration['SOURCEURL'] = parser.get('hostscraper', 'SOURCEURL')

    if _args.QUERY:
        configuration['QUERY'] = _args.QUERY
    else:
        configuration['QUERY'] = parser.get('hostscraper', 'QUERY')
    LOG.debug('Doing things with %s', configuration['SOURCEURL'])
    LOG.debug('leaving get_config')
    return configuration


def get_args():
    """ we only run if called from main """
    _args = get_options()

    if _args.debug:
        LOG.setLevel(logging.DEBUG)
    else:
        LOG.setLevel(logging.WARN)
    return _args


# Here we start if called directly (the usual case.)
if __name__ == "__main__":
    # This is where we will begin when called from CLI. No need for argparse
    # unless being called interactively, so import it here
    args = get_args()
    # and now we can do, whatever it is, we do.
    sys.exit(run(args))
