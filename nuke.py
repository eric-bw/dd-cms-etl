import sys
if sys.version_info < (3, 0):
    sys.stdout.write("Sorry, this software requires Python 3.7, not Python " + str(sys.version_info.major) + '.' +  str(sys.version_info.minor) + "\n")
    sys.exit(1)

import _lib
from simple_salesforce import Salesforce
import argparse
import datetime
import csv


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
                    required=False,
                    default=True)

parser.add_argument('-o', '--object',
                    nargs='+',
                    help=' Options [CMS_Mega_Menu__c, CMS_Page__c, CMS_Collection__c, CMS_Asset__c]',
                    required=False,
                    default=None)


args = parser.parse_args(sys.argv[1:])


target = Salesforce(username=args.username, password=args.password, sandbox=args.sandbox, security_token=args.token)


input('WARNING: this will delete all CMS data on the target org. press enter to continue or ctrl-C to cancel')
_lib.clear_content(target, args.object)