#!/usr/bin/env python

"""Test the external hosts concept."""

import sys
import os
import collections
import json
import fnmatch

inventory_data_files = ["hosts.inv"]

all_stages = ["dev", "qa", "prod"]
all_groups = collections.OrderedDict()
all_hosts = collections.OrderedDict()
hosts_by_name = collections.OrderedDict()


def server(url, name,
           ip4="",
           hostname="",
           stage="",
           provider="",
           groups=[],
           status="",
           description="",
           variables={}
           ):
    """Structure server information into a dictionary."""
    if url not in all_hosts:
        print "url not unique"
    result = dict(stage=stage,
                  groups=tuple(groups),  # order affects variable inclusion
                  provider=provider,
                  url=url,
                  hostname=hostname or url,
                  variables=variables)
    all_hosts[url] = result

for name in inventory_data_files:
    execfile(name)


class Hosts(object):
    """Collects and lists hosts for ansible.
    Poor man's configuration database."""

    def __init__(self, hostdict):
        self.all = hostdict

    def itergroups(self, filtered=False):
        """Ordinally steps through the groups in url,group order.

        yields: url, group
        """
        hosts = self.filtered() if filtered else self.all
        for url, info in hosts:
            for group in info["groups"]:
                yield url, group

    def filtered(self):
        """yields all hosts' items, filtered by environment variables:
        ANSIBLE_STAGEFILTER = all, dev, qa, or prod
        ANSIBLE_GROUPFILTER = comma,separated,group,names
        ANSIBLE_HOSTFILTER = hostnameglob
        These are AND filters if specified.

        yields: key, value
        """
        stage = os.getenv("ANSIBLE_STAGEFILTER")
        if stage is None:
            raise StandardError("Must specify the ANSIBLE_STAGEFILTER env.")
        stages = stage.split(",")
        groups = os.getenv("ANSIBLE_GROUPFILTER")
        groups = set(groups.split(",")) if groups else set([])

        hosts = os.getenv("ANSIBLE_HOSTFILTER", "*")

        def passes_filter(s):
            "s = server info dict"
            # filter by stage
            if s["stage"] not in stages:
                return False
#            # filter by groups
#            mygroups = set(info["groups"])
#            if bool(groups):
#                if bool( groups & mygroups):
#                    pass
#                else:
#                    return False
            #filter by hostname/url
            return fnmatch.fnmatchcase(info["url"], hosts) or fnmatch.fnmatchcase(info["hostname"], hosts)
            #return True

        for url, info in self.all.items():
            if passes_filter(info):
                yield (url, info)

    def groups(self, filtered=True):
        result = collections.OrderedDict()
        for url, group in self.itergroups(filtered=filtered):
            if group not in result:
                result[group] = [url]
            else:
                result[group].append(url)
        return result

    def listgroups(self):
        return json.dumps(self.groups(filtered=True))

    def injectvars(self, url):
        info = self.all[url]
        explicit_vars = info["variables"]
        infovars = dict(groups=",".join(info["groups"]),
                        url=info["url"],
                        hostname=info["hostname"],
                        provider=info["provider"],
                        )
        v = {}
        #inject group vars
        v.update(infovars)
        v.update(explicit_vars)
        info["variables"] = v

    def listvars(self, url):
        self.injectvars(url)  # add group and instance info into vars
        return json.dumps(self.all[url]["variables"])

    def report(self, format="text"):
        #import pdb; pdb.set_trace()
        for url, info in self.all.items():
            info["groups"] = list(info["groups"])
            str_format = """|%(stage)-5s |%(hostname)-50s |@%(url)s |"""
            record = str_format
            yield record % info


def fail(msg, *args):
    print msg
    sys.exit(1)


def run():
    args = sys.argv
    if len(args) < 2:
        print "supply --list, --host <host>, --report"
        sys.exit(1)
    try:
        hosts = Hosts(all_hosts)
        if args[1] == "--list":
            print hosts.listgroups()
        elif args[1] == "--host":
            print hosts.listvars(args[2])
        elif args[1] == "--report":
            format = "text"
            print "\n".join(hosts.report(format))
        else:
            fail("inventory.py called with bad arguments", args)
    except Exception, e:
        import traceback
        traceback.print_exc()
        fail("exception in inventory.py %s" % e.message, {})


if name == "__main__":
    # Called directly
    import argparse
    parser = argparse.ArgumentParser(
        description='Returns results of inventory query')
    parser.add_argument('-n', '--dryrun', action='store_true',
        help='Dry run, do not actually perform action', default=False)
    parser.add_argument('-d', '--debug', action='store_true',
        help='Enable debugging during execution.', default=None)
    parser.add_argument('-r', '--readable', action='store_true', default=False,
        help='Display output in human readable formant (as opposed to json).')
    parser.add_argument('-c', '--config', action='store', default=None,
        help='Specify a path to an alternate config file')

    run()
