import _lib
from simple_salesforce import Salesforce
import argparse
import sys
import datetime
import csv
import re


parser = argparse.ArgumentParser(description='transfer content from a specifically designed excel document into a new org')

parser.add_argument('-i', '--input',
                    help=' input',
                    required=True)

parser.add_argument('-u', '--username',
                    help=' Username',
                    required=True)

parser.add_argument('-p', '--password',
                    help=' Password',
                    required=True)

parser.add_argument('-t', '--token',
                    help=' Token',
                    required=False,
                    default='')

parser.add_argument('-s', '--sandbox',
                    type=_lib.str2bool,
                    help=' is sandbox',
                    required=True,
                    default=True)

parser.add_argument('-d', '--debug',
                    type=_lib.str2bool,
                    help=' Debug output',
                    required=False,
                    default=False)


args = parser.parse_args(sys.argv[1:])

print('Items to remember!: 1) your user needs to be an administrator (to access the Asset Library).\n 2) your user needs to have the Portal CMS Editor Permission set.')
target = Salesforce(username=args.username, password=args.password, sandbox=args.sandbox, security_token=args.token, version='44.0')

log = csv.writer(open('./' + 'log_' +  args.username.split('@')[1]  + re.sub('[^A-z0-9]','_', '_'+ str(datetime.datetime.now())) + '.csv','w'))
log.writerow(['ORIGINAL_ID','NEW_ID','Notes'])
_lib.transfer(args.input, target, log, args)