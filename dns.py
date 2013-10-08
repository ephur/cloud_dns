#!/usr/bin/env python

import pyrax
import sys
import os
import ConfigParser
import argparse
import time

try:
    from keyczar import keyczar
    KEYCZAR = True
except ImportError:
    KEYCZAR = False

try:
    import keyring
    import getpass
    import re
    KEYRING = True
except ImportError:
    KEYRING = False


PROG_DESCRIPTION="""A utility to simplify working with our DNS As A Service.
Please keep in mind some operations take awhile to complete thanks to our
large number of resources, and having to make dozens of API calls for some of
the requests. Doing operations for all domains on the account can take a very long
time when all domains have to be retrieved, one page of records at a time."""
PROG_WARNING="This program makes changes to the production DNS systems.\
Please exercise extreme caution when making changes to DNS"
VERSION=0.1
RECORD_TYPES=['PTR','A','AAAA','CNAME','TXT']
VERBOSE=False

def main(*args, **kwargs):
    arg = args[0]
    try:
        dns = dnsActions(arg.username, arg.apikey, arg.verbose)
    except pyrax.exceptions.AuthenticationFailed:
        print "ERROR Unable to authenticate, check your config/credentials"
    return getattr(dns, arg.action)(arg)

def do_config():
    parser = argparse.ArgumentParser(description=PROG_DESCRIPTION,
                                     epilog=PROG_WARNING,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-c","--config-file", help="configuration file for dns script", type=str, default="config.ini")
    parser.add_argument("-k","--keypath", help="path to keyczar keys if apikey is encrpyted, can be specified in config file", default=None)
    parser.add_argument("--tenant", help="Tenant (DDI) to operate on. Can be specified in config file.", default=None)
    parser.add_argument("--username", help="Username to authenticate with. Can be specified in config file.", default=None)
    parser.add_argument("--verbose", help="more verbose output in random places!", action="store_true")
    parser.add_argument("--apikey", help="API key to use. Can be specified in config file, assumed encrypted if keypath specified", default=None )
    parser.add_argument("--update-keychain", help="prompt to update keychain entries (if you're using them!)", action="store_true")
    parser.add_argument("-v","--version", action="version", version='%(prog)s ' + str(VERSION))

    subparsers = parser.add_subparsers(dest="action")
    parser_add_domain = subparsers.add_parser('add_domain', help="add a domain to the DNS system")
    parser_add_domain.add_argument('domain', help='domain name to add')

    parser_delete_domain = subparsers.add_parser('delete_domain', help="remove a domain from the DNS system")
    parser_delete_domain.add_argument('domain', help='domain name to delete')

    parser_list_domains = subparsers.add_parser('list_domains', help="list all domains on the account")

    parser_add_record = subparsers.add_parser('add_record', help="add a new record")
    parser_add_record.add_argument('domain', help='domain to add record to')
    parser_add_record.add_argument('name', help='the fully qualifed DNS record/hostname')
    parser_add_record.add_argument('target', help='ip address')
    parser_add_record.add_argument('type', help='type of record')
    parser_add_record.add_argument('-t','--ttl', help='ttl, default 300')
    parser_add_record.add_argument('-p','--priority', help='priority (for MX recrods only)')
    parser_add_record.add_argument('-c','--comment', help='comment associated with record')

    parser_add_bulk = subparsers.add_parser('add_bulk', help="add a bunch of records")
    parser_add_bulk.add_argument('record', help="record in the form of NAME:TYPE:TARGET (www.foo.com:A:192.168.1.100 wiki.foo.com:CNAME:www.foo.com)", nargs='*')
    parser_add_bulk.add_argument('--from-file', help="read records from a file, in the same format, one record per line in the file")

    parser_list_records = subparsers.add_parser('list_records', help="list all records in a zone")
    parser_list_records.add_argument('domain', help='domain name(s) to list records for',nargs='*')
    parser_list_records.add_argument('--type', '-t', help="record type (CNAME/A), etc...")
    parser_list_records.add_argument('--data', '-d', help='Data (IP4/IP6 or CNAME Destination to match)')
    parser_list_records.add_argument('--name', '-n', help='Name to match (or partial name to match)')

    args = parser.parse_args()
    return main_validate(args)

def main_validate(args):
    # If a config file is specified, then get values from it
    if args.config_file is not None:
        config = ConfigParser.ConfigParser()
        try:
            config.readfp(open(args.config_file))
        except IOError as e:
            raise IOError("Unable to read configuration file %s" % (args.config_file))

    # Validate that required items are either in config file or on command line
    for item in ['username', 'apikey', 'tenant']:
        if getattr(args, item) is None:
            if args.config_file is None:
                raise ValueError("Must specify %s option, or put it in a config file and specify config file"  %(item))
            else:
                try:
                    setattr(args,item,config.get("cloud_dns",item))
                except (ConfigParser.NoOptionError, ConfigParser.NoSectionError) as e:
                    raise ValueError("%s not found in configuration file and option not specified" %(item))

    # For the following values, see if they are stored in the system keyring, use those values if they are
    for item in ['username', 'apikey', 'tenant']:
        if getattr(args,item).upper().startswith("USE_KEYRING"):
            try:
                (appname, value) = re.findall('^USE_KEYRING\[\'(.*)\'\]$', getattr(args,item),re.IGNORECASE)[0].split(":")
                if args.update_keychain is True:
                    print "Updating %s in keychain %s:%s (leave blank to leave current value)" % (item.upper(), appname, value)
                    retval = raw_input ("Enter value (WARNING INPUT IS ECHOED TO TERMINAL):")
                    if retval != "":
                        keyring.set_password(appname, value, retval)
                retval = keyring.get_password(appname, value)
                if retval is None:
                    print "ERROR: Can't get %s from the keychain %s:%s" % (item.upper(), appname, value)
                    retval = raw_input("Enter value to store in keychain (WARNING INPUT IS ECHOED TO TERMINAL):")
                    keyring.set_password(appname, value, retval)
                setattr(args, item, retval)

            except (IndexError, ValueError) as e:
                print "ERROR: Looks like you want to use the keyring, but don't have a proper value setup. The config item should look like: %s=USE_KEYRING['appname:value']" % (item)
                sys.exit(1)

    # Set the keypath argument if it's found in the config file
    if (args.keypath is None) and (args.config_file is not None):
        try:
            args.keypath = config.get("cloud_dns", "keypath")
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError) as e:
            pass

    # Finally decrypt any items that are stored encrypted
    if (args.keypath is not None) and (KEYCZAR is True):
        crypter = keyczar.Crypter.Read(args.keypath)
        for item in ['username', 'apikey', 'tenant']:
            try:
                val = crypter.Decrypt(getattr(args, item))
                setattr(args,item,val)
            except (keyczar.errors.Base64DecodingError, keyczar.errors.BadVersionError, keyczar.errors.ShortCiphertextError):
                pass

    return args

class dnsActions:
    def __init__(self, username, apikey, verbose):
        pyrax.set_setting("identity_type", "rackspace")
        pyrax.set_credentials(username, apikey)
        self.dns = pyrax.cloud_dns
        self.verbose = verbose
        self.domains = None

        if self.domains is not None:
            return self

    def list_domains(self,*args):
        if self.domains is None:
            self.domains = self._get_domains()

        for item in sorted(self.domains):
            if self.verbose is True:
                print "%s (id=%s, email_address=%s) " % (item.name, item.id, item.emailAddress)
            else:
                print "%s" % (item.name)

        return 0

    def list_records(self, *args):
        arg = args[0]
        domains = list()

        if len(arg.domain) == 0:
            [arg.domain.append(x.name) for x in self._get_domains()]

        # Have to convert the domains to the numeric ID's
        for domain in arg.domain:
            all_records = list()
            try:
                domain_id = int(domain)
            except ValueError:
                domain_id = self._get_domain_id(domain)

            [all_records.append(x) for x in self.dns.get_record_iterator(domain_id)]

            for item in all_records[:]:
                if (arg.type is not None) and (item.type.upper() != arg.type.upper()):
                    all_records.remove(item)
                    continue
                if (arg.name is not None) and (arg.name.upper() not in item.name.upper()):
                    all_records.remove(item)
                    continue
                if (arg.data is not None) and (arg.data.upper() not in item.data.upper()):
                    all_records.remove(item)
                    continue

            maxname, maxttl, maxtype, maxdata = 0, 0, 0, 0
            for item in all_records:
                maxname = max(maxname, len(item.name))
                maxttl = max(maxttl, len(str(item.ttl)))
                maxtype = max(maxtype, len(item.type))
                maxdata = max(maxdata, len(item.data))

            print "displaying %d matching records for %s (domain ID: %s) " % (len(all_records), domain, domain_id)
            for item in all_records:
                print "%-*s  %-*s  %-*s  %-*s" % (maxname, item.name, maxttl, str(item.ttl), maxtype, item.type, maxdata, item.data)
            print ""

        return 0

    def _get_domain_id(self,domain):
        if self.domains is None:
            self._get_domains()
        for a_domain in self.domains:
            if a_domain.name == domain:
                return a_domain.id
        raise ValueError("unable to find ID for domain: %s" %(domain))

    def _get_domains(self):
        """ Get a listing of all the domains """
        if self.domains is None:
            domains = list()
            for item in self.dns.get_domain_iterator():
                domains.append(item)
            self.domains = domains
        return self.domains

if __name__ == "__main__":
    sys.exit(main(do_config()))