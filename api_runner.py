import sys
if sys.version_info < (3, 0):
    sys.stdout.write("Sorry, this software requires Python 3(.7), not Python " + str(sys.version_info.major) + '.' +  str(sys.version_info.minor) + "\n")
    sys.exit(1)

from openpyxl import load_workbook, Workbook
import datetime
import _lib
import zipfile


import argparse
import sys

import re
from simple_salesforce import Salesforce
import difflib

from simple_salesforce import SalesforceGeneralError
from collections import OrderedDict


parser = argparse.ArgumentParser(description='transfer content from a specifically designed excel document into a new org')

parser.add_argument('-i', '--input',
                    help=' input',
                    required=True)

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

def exec_anon(self, apex_string):
    """Executes a string of Apex code."""
    url = self.base_url  +  "tooling/executeAnonymous/"
    params = {'anonymousBody': apex_string}
    result = self.request.get(url, headers=self.headers, params=params)
    if result.status_code != 200:
        raise SalesforceGeneralError(url,
                                     'executeAnonymous',
                                     result.status_code,
                                     result.content)
    json_result = result.json(object_pairs_hook=OrderedDict)
    if len(json_result) == 0:
        return None
    else:
        return json_result



args = parser.parse_args(sys.argv[1:])
Salesforce.exec_anon = exec_anon
sf = Salesforce(username=args.username, password=args.password, sandbox=args.sandbox, security_token=args.token, version='44.0')


wb = load_workbook(args.input)
sheet = wb.active
for i, row in enumerate(sheet.rows):
    if i > 1:
        if row[1].value and row[1].value != 'Member ID':
            dob = row[4].value
            # rs = sf.query('select Id, Name from Member__c where name = \'0' + str(row[0].value) + '\'')['records']
            # if not rs:
            #     rs = sf.Member__c.create({'Name': '0' + str(row[0].value), 'First_Name__c': row[3].value,
            #                               'Last_Name__c': row[2].value,
            #                               'Date_Of_Birth__c': row[4].value.strftime('%Y-%m-%d'),
            #                               'Dependent_No__c':'1',
            #                               'Group_Number__c':'1234',
            #                               'Product_Category__c': 'Dental',
            #                               'Zip__c': row[5].value
            #                               })
            #     print(rs)
            # else:
            #     rs = sf.Member__c.update(rs[0]['Id'], {'Name': '0' + str(row[0].value), 'First_Name__c': row[3].value,
            #                               'Last_Name__c': row[2].value,
            #                               'Date_Of_Birth__c': row[4].value.strftime('%Y-%m-%d'),
            #                               'Dependent_No__c':'1',
            #                               'Group_Number__c':'1234',
            #                               'Product_Category__c': 'Dental',
            #                               'Zip__c': row[5].value
            #                               })

            rs = sf.exec_anon("""
SP_CMSModel.RegistrationRequest request = new SP_CMSModel.RegistrationRequest();
request.subscriberid = '%s';
request.firstname = '%s';
request.lastname = '%s';
request.dateofbirth = '%s';
system.debug(SP_CMSUserService.verifyRegistration(request));"""%(
                row[1].value,row[3].value,row[2].value,dob.strftime('%Y-%m-%d')))

