Cloud DNS Tool
=========
A script to make working with Cloud DNS quicker

## Requires
PyRax -- PIP Installed Rackspace Python LIB for interacting with cloud services
KeyCzar -- Optional, if storing encrypted credentials/values

## Configuration File
All configuration options can be passed on the command line, but a configuration file will make things easier.

``
[cloud_dns]
tenant = Tenant/DDI
username = Username with access to tenant/ID
apikey = APIKey for the Username
keypath = Optional Value if keyczar is installed, you wish to encrypt items in the config file
``

## Using KeyCzar
These are all done after a pip install of keyczar, or using OS packages to install (preferred on Debian/RHEL)
* Choose a path for keys, this is what keypath in the config file will be set to
``` export KEYPATH="/Users/ephur/Projects/CloudServers/src/cloud_dns/etc/keys" ```
* Make the directory
``` mkdir -p ${KEYPATH} ```
* Create the keystore
``` keyczart create --location=${KEYPATH} --purpose=crypt --name="cloud_dns" ```
* Create a key
``` keyczart addkey --location=${KEYPATH} --status=primary ```
* Then you can use the included script to encrypt your config values:
``` python ./crypt_string.py ${KEYPATH}
Password:
Note, the beginning and ending COLON are not part of your crypted string
The crypted string is :ADQZJPu-ovb-lAdCuXyeixsoBBXYTmuGiLRy6Zn3IhOF2YOQ8cjru3-b5xithoVhignLRyKX_w8b: ```

## How To use the tool
* Basic usage
```./dns.py --help
usage: dns.py [-h] [-c CONFIG_FILE] [-k KEYPATH] [--tenant TENANT]
              [--username USERNAME] [--verbose] [--apikey APIKEY] [-v]
              {add_record,add_domain,list_records,delete_domain,list_domains}
              ...

A utility to simplify working with our DNS As A Service. Please keep in mind
some operations take awhile to complete thanks to our large number of
resources, and having to make dozens of API calls for some of the requests.
Doing operations for all domains on the account can take a very long time when
all domains have to be retrieved, one page of records at a time.

positional arguments:
  {add_record,add_domain,list_records,delete_domain,list_domains}
    add_domain          add a domain to the DNS system
    delete_domain       remove a domain from the DNS system
    list_domains        list all domains on the account
    add_record          add a new record
    list_records        list all records in a zone

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        configuration file for dns script (default:
                        config.ini)
  -k KEYPATH, --keypath KEYPATH
                        path to keyczar keys if apikey is encrpyted, can be
                        specified in config file (default: None)
  --tenant TENANT       Tenant (DDI) to operate on. Can be specified in config
                        file. (default: None)
  --username USERNAME   Username to authenticate with. Can be specified in
                        config file. (default: None)
  --verbose             more verbose output in random places! (default: False)
  --apikey APIKEY       API key to use. Can be specified in config file,
                        assumed encrypted if keypath specified (default: None)
  -v, --version         show program's version number and exit

This program makes changes to the production DNS systems.Please exercise
extreme caution when making changes to DNS ```
