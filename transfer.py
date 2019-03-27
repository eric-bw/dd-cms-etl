import _lib
from simple_salesforce import Salesforce
import argparse
import sys
import datetime
import csv


parser = argparse.ArgumentParser(description='transfer content from a specifically designed excel document into a new org')

parser.add_argument('-i', '--input',
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
                    type=_lib.str2bool,
                    help=' is sandbox',
                    required=False,
                    default=True)

parser.add_argument('-r', '--refresh',
                    type=_lib.str2bool,
                    help='clear data before loading',
                    required=False,
                    default=False)


args = parser.parse_args(sys.argv[1:])


target = Salesforce(username=args.username, password=args.password, sandbox=args.sandbox, security_token=args.token)

log = csv.writer(open('./' + 'log_' +  args.username  +'_'+ str(datetime.datetime.now()) + '.csv','w'))
log.writerow(['ORIGINAL_ID','NEW_ID','Notes'])
_lib.transfer(args.input, target, log)