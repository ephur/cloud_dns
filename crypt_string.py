#!/usr/bin/env python
import sys
import getpass
from keyczar import keyczar

def main():
	try:
	    path_to_keys = str(sys.argv[1])
	except IndexError:
		print "Excpected usage: %s /path/to/keyczar_key" % (sys.argv[0])
		return 1

	crypter = keyczar.Crypter.Read(path_to_keys)
	# string = raw_input("String to crypt: ")
	string = getpass.getpass()
	print "Note, the beginning and ending COLON are not part of your crypted string"
	print "The crypted string is :%s:" % (crypter.Encrypt(string))
	return 0

if __name__ == "__main__":
  sys.exit(main())
