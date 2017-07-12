#! /usr/bin/env python

import sys
import requests

def main():
    resp = requests.get("http://%s" % sys.argv[1])
    if resp.ok:
	sys.exit(0)
    sys.exit(1)

if __name__ == '__main__':
    main()
