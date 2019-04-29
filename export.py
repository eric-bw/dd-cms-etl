import sys
if sys.version_info < (3, 0):
    sys.stdout.write("Sorry, this software requires Python 3(.7), not Python " + str(sys.version_info.major) + '.' +  str(sys.version_info.minor) + "\n")
    sys.exit(1)

import _lib
import datetime
from simple_salesforce import Salesforce

import argparse
import sys


parser = argparse.ArgumentParser(description='transfer content from a specifically designed excel document into a new org')

parser.add_argument('-u', '--username',
                    help=' Username',
                    required=True,
                    default='.')

parser.add_argument('-p', '--password',
                    help=' Password',
                    required=True,
                    default='.')

parser.add_argument('-t', '--token',
                    help=' Token',
                    required=False,
                    default='')

parser.add_argument('-s', '--sandbox',
                    type=_lib.str2bool,
                    help=' is sandbox',
                    required=True,
                    default=True)

parser.add_argument('-pages', '--pages',
                    nargs='+',
                    help='export only pages and related content',
                    required=False)

parser.add_argument('-mega', '--mega',
                    nargs='+',
                    help='export only mega menu and related content',
                    required=False)


args = parser.parse_args(sys.argv[1:])


print('Items to remember!: 1) your user needs to be an administrator (to access the Asset Library).\n 2) your user needs to have the Portal CMS Editor Permission set.')
dev = Salesforce(username=args.username, password=args.password, sandbox=args.sandbox, security_token=args.token)
_lib.output(dev, 'contentpak_' + args.username.split('@')[1]   + '_' + datetime.datetime.now().strftime('%y-%m-%d'), args)