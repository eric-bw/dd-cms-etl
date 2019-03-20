import lib
import datetime
from simple_salesforce import Salesforce

import argparse
import sys


parser = argparse.ArgumentParser(description='transfer content from a specifically designed excel document into a new org')

parser.add_argument('-o', '--output',
                    help=' input',
                    required=False,
                    default='')

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
                    type=lib.str2bool,
                    help=' is sandbox',
                    required=False,
                    default=True)


args = parser.parse_args(sys.argv[1:])

dev = Salesforce(username=args.username, password=args.password, sandbox=args.sandbox, security_token=args.token)

if args.output:
    path = args.output
else:
    path = './export.' + datetime.datetime.now().strftime('%y-%m-%d') + '.xlsx'

lib.output(dev, path)
print('done')