import sys
if sys.version_info < (3, 0):
    sys.stdout.write("Sorry, this software requires Python 3(.7), not Python " + str(sys.version_info.major) + '.' +  str(sys.version_info.minor) + "\n")
    sys.exit(1)

import _lib
import datetime
from simple_salesforce import Salesforce

import argparse
import csv
import re




parser = argparse.ArgumentParser(description='transfer content from a specifically designed excel document into a new org')

parser.add_argument('-a', '--action',
                    help='',
                    required=True,
                    default='breakdown')


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




args = parser.parse_args(sys.argv[1:])


def write_match(csv, o, oname, id, field,  match):
    if(len(match.groups()) == 2):
        label = match.groups()[0]
        link = match.groups()[1]
    else:
        label = ''
        link = match.groups()[0]
    coords = match.regs
    is_mega = False

    if 'CMS_Mega_Menu__c' in o and o['CMS_Mega_Menu__c'] is not None:
        is_mega = True
    if 'Collection__r' in o and  o['Collection__r'] is not None and o['Collection__r']['CMS_Mega_Menu__c'] is not None:
        is_mega = True

    values = [oname, id, 'https://deltadentalwi--coredx.lightning.force.com/lightning/r/' + oname + '/' + id + '/view', is_mega,  field, str(coords), label, link]
    print(values)
    csv.writerow(values)

def write_link(csv,o, oname, id, field,label, value):
    is_mega = False
    if 'CMS_Mega_Menu__c' in o and o['CMS_Mega_Menu__c'] is not None:
        is_mega = True
    if 'Collection__r' in o and o['Collection__r'] is not None and o['Collection__r']['CMS_Mega_Menu__c'] is not None:
        is_mega = True
    values = [oname, id, 'https://deltadentalwi--coredx.lightning.force.com/lightning/r/' + oname + '/' + id + '/view', is_mega, field, '', label, value]
    print(values)
    csv.writerow(values)

def write_mega(csv,o, oname, id, field,label, value):
    values = [oname, id, 'https://deltadentalwi--coredx.lightning.force.com/lightning/r/' + oname + '/' + id + '/view', True, field, '', label, value]
    print(values)
    csv.writerow(values)

def breakdown(sf):
    f = csv.writer(open('links.csv','w'))
    f.writerow(['Object','ID', 'Link', 'Mega Menu', 'Field','Coordinates','Label', 'href'])
    fields = '''Id, slug__c, Title__c, RecordType.Name, Name, body__c, link__c, link_text__c, CMS_Mega_Menu__c, Collection__r.CMS_Mega_Menu__c '''
    for content in sf.query_all('select ' + fields + ' ,(select ' + fields + ' from Contents__r) from CMS_Content__c')['records']:
        if content['Body__c']:
            for m in re.finditer('\[(.*?)\]\((.*?)\)', content['Body__c']):
                write_match(f, content, 'CMS_Content__c', content['Id'], 'Body__c', m)
            for m in re.finditer('href="(.*?)"', content['Body__c']):
                write_match(f, content, 'CMS_Content__c', content['Id'], 'Body__c', m)
            if(content['Link_Text__c']):
                write_link(f, content, 'CMS_Content__c',content['Id'], 'link__c', content['Link_Text__c'], content['link__c'])
            elif(content['RecordType']['Name'] == 'Mega Menu Content'):
                write_mega(f, content, 'CMS_Content__c',content['Id'], 'link__c', content['Title__c'], content['link__c'])

        if content['Contents__r']:
            for child in content['Contents__r']['records']:
                if child['Body__c']:
                    for m in re.finditer('\[(.*?)\]\((.*?)\)', child['Body__c']):
                        write_match(f, child,  'CMS_Content__c', child['Id'], 'Body__c', m)
                    for m in re.finditer('href="(.*?)"', child['Body__c']):
                        write_match(f, child, 'CMS_Content__c', content['Id'], 'Body__c', m)
                if(child['Link_Text__c']):
                    write_link(f, child, 'CMS_Content__c',child['Id'], 'Link__c', child['Link_Text__c'], child['link__c'])
                elif(child['RecordType']['Name'] == 'Mega Menu Content'):
                    write_mega(f, child, 'CMS_Content__c',child['Id'], 'link__c', child['Title__c'], child['link__c'])




    for page in sf.query_all('select Id, breadcrumb__c,Broker_Breadcrumb__c,slug__c, Employer_Breadcrumb__c,Provider_Breadcrumb__c, Member_Mobile_breadcrumb__c,Broker_Mobile_Breadcrumb__c,Employer_Mobile_Breadcrumb__c,Provider_Mobile_Breadcrumb__c from CMS_Page__c')['records']:
        for m in re.finditer('\[(.*?)\]\((.*?)\)', str(page['breadcrumb__c'])):
            write_match(f, page, 'CMS_Page__c', page['Id'], 'breadcrumb__c', m)
        for m in re.finditer('\[(.*?)\]\((.*?)\)', str(page['Broker_Breadcrumb__c'])):
            write_match(f, page, 'CMS_Page__c', page['Id'], 'Broker_Breadcrumb__c', m)
        for m in re.finditer('\[(.*?)\]\((.*?)\)', str(page['Employer_Breadcrumb__c'])):
            write_match(f, page, 'CMS_Page__c', page['Id'], 'Employer_Breadcrumb__c', m)
        for m in re.finditer('\[(.*?)\]\((.*?)\)', str(page['Provider_Breadcrumb__c'])):
            write_match(f, page, 'CMS_Page__c', page['Id'], 'Provider_Breadcrumb__c', m)
        for m in re.finditer('\[(.*?)\]\((.*?)\)', str(page['Member_Mobile_Breadcrumb__c'])):
            write_match(f, page, 'CMS_Page__c', page['Id'], 'Member_Mobile_Breadcrumb__c', m)
        for m in re.finditer('\[(.*?)\]\((.*?)\)', str(page['Broker_Mobile_Breadcrumb__c'])):
            write_match(f, page, 'CMS_Page__c', page['Id'], 'Broker_Mobile_Breadcrumb__c', m)
        for m in re.finditer('\[(.*?)\]\((.*?)\)', str(page['Employer_Mobile_Breadcrumb__c'])):
            write_match(f, page, 'CMS_Page__c', page['Id'], 'Employer_Mobile_Breadcrumb__c', m)
        for m in re.finditer('\[(.*?)\]\((.*?)\)', str(page['Provider_Mobile_Breadcrumb__c'])):
            write_match(f, page, 'CMS_Page__c', page['Id'], 'Provider_Mobile_Breadcrumb__c', m)








sf = Salesforce(username=args.username, password=args.password, sandbox=args.sandbox, security_token=args.token)

if args.action == 'breakdown':
    breakdown(sf)

