Cloud DNS Tool
=========
A script to make working with Cloud DNS quicker

## Requires
PyRax -- PIP Installed Rackspace Python LIB for interacting with cloud services
KeyCzar -- Optional, if storing encrypted credentials/values

## Installing
The install relies on setup tools. If you already have setup tools it's as easy as:

```
python ./setup.py install 
``` 

If not, you will need to add setup tools, there's a few ways to do it. Check out https://pypi.python.org/pypi/setuptools#installing-and-using-setuptools

## Configuration File
All configuration options can be passed on the command line, but a configuration file will make things easier. If no configuration is specified on the command line (via the -c/--config-file) then $HOME/.cloud\_dns.ini will be used (if it exists!)

```
[cloud_dns]
tenant = Tenant/DDI
username = Username with access to tenant/ID
apikey = APIKey for the Username
keypath = Optional Value if keyczar is installed, you wish to encrypt items in the config file
```

If you're using OSX and want to store values in the OSX System KeyChain then your config would look a little something like this:

```
[cloud_dns]
tenant = USE_KEYRING['cloud_dns:tenant']
username = USE_KEYRING['cloud_dns:username']
apikey = USE_KEYRING['cloud_dns:apikey']
```

You can still use KeyCzar encryption with items stored in the keychain, just include a keypath configuration item, and those keys will be used to try and decrypt values that are returned from the keychain. 

## Using KeyCzar
These are all done after a pip install of keyczar, or using OS packages to install (preferred on Debian/RHEL)
* Choose a path for keys, this is what keypath in the config file will be set to
```
export KEYPATH="/Users/ephur/Projects/CloudServers/src/cloud_dns/etc/keys"
```
* Make the directory
```
mkdir -p ${KEYPATH}
```
* Create the keystore
```
keyczart create --location=${KEYPATH} --purpose=crypt --name="cloud_dns"
```
* Create a key
```
keyczart addkey --location=${KEYPATH} --status=primary
```
* Then you can use the included script to encrypt your config values:

```
./crypt_string.py ${KEYPATH}
Password:
Note, the beginning and ending COLON are not part of your crypted string
The crypted string is :abunchofjunk:
```

## How To use the tool

#### Main Usage

```
usage: dns.py [-h] [-c CONFIG_FILE] [-k KEYPATH] [--tenant TENANT]
              [--username USERNAME] [--verbose] [--apikey APIKEY]
              [--update-keychain] [-v]

              {add_domain,list_domains,list_subdomains,delete_domain,add_record,add_bulk,list_records}
              ...

A utility to simplify working with our DNS As A Service. Please keep in mind
some operations take awhile to complete thanks to our large number of
resources, and having to make dozens of API calls for some of the requests.
Doing operations for all domains on the account can take a very long time when
all domains have to be retrieved, one page of records at a time.

positional arguments:
  {add_domain,list_domains,list_subdomains,delete_domain,add_record,add_bulk,list_records}
    add_domain          add a domain to the DNS system
    list_domains        list all domains on the account
    list_subdomains     list the subdomains for a domain
    delete_domain       remove a domain from the DNS system
    add_record          add a new record
    add_bulk            add a bunch of records
    list_records        list all records in a zone

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        configuration file for dns script (default:
                        ~/.cloud_dns.ini) (default: None)
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
  --update-keychain     prompt to update keychain entries (if you're using
                        them!) (default: False)
  -v, --version         show program's version number and exit

This program makes changes to the production DNS systems.Please exercise
extreme caution when making changes to DNS
```

#### Adding Records 

```
usage: dns.py add_record [-h] [-t TTL] [-p PRIORITY] [-c COMMENT]
                         domain name target type

positional arguments:
  domain                domain to add record to
  name                  the fully qualifed DNS record/hostname
  target                ip address
  type                  type of record

optional arguments:
  -h, --help            show this help message and exit
  -t TTL, --ttl TTL     ttl, default 300
  -p PRIORITY, --priority PRIORITY
                        priority (for MX recrods only)
  -c COMMENT, --comment COMMENT
                        comment associated with record
```

#### Bulk Adding Records 

To add a lot of records use the add_bulk command, you can add as many records as you want. In the format of name,type,target. One item per line in a file and as many pairs on the command line as you like. The options ttl and priority apply to all records (if applicable) when creating them. If one record fails validation, NO records will be added.

```
usage: dns.py add_bulk [-h] [--from-file FROM_FILE] [-t TTL] [-p PRIORITY]
                       domain [record [record ...]]

positional arguments:
  domain                domain to add record into
  record                record in the form of NAME:TYPE:TARGET
                        (www.foo.com,A,192.168.1.100
                        wiki.foo.com,CNAME,www.foo.com), specify as many as
                        you want

optional arguments:
  -h, --help            show this help message and exit
  --from-file FROM_FILE
                        read records from a file, in the same format, one
                        record per line in the file
  -t TTL, --ttl TTL     the TTL for all records added, default is 3600,
                        minimum is 300
  -p PRIORITY, --priority PRIORITY
                        priority for any MX records, default 10
```
