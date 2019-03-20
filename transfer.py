import lib
from simple_salesforce import Salesforce
import argparse
import sys
import datetime


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
                    type=lib.str2bool,
                    help=' is sandbox',
                    required=False,
                    default=True)

parser.add_argument('-r', '--refresh',
                    type=lib.str2bool,
                    help='clear data before loading',
                    required=False,
                    default=True)


args = parser.parse_args(sys.argv[1:])


target = Salesforce(username=args.username, password=args.password, sandbox=args.sandbox, security_token=args.token)
log = './' + args.username + '_log_' + str(datetime.datetime.now()) + '.xlsx'

if args.refresh:
    lib.clear_content(target)
lib.transfer(args.input, target, log)



