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
from openpyxl import load_workbook, Workbook





parser = argparse.ArgumentParser(description='transfer content from a specifically designed excel document into a new org')

parser.add_argument('-a', '--action',
                    help='',
                    required=True,
                    default='breakdown')

parser.add_argument('-c', '--content',
                    help=' content',
                    required=False)

parser.add_argument('-i', '--input',
                    help=' input',
                    required=False)

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

def write_link(csv,o, oname, id, field,label, value, options):
    is_mega = False
    if 'CMS_Mega_Menu__c' in o and o['CMS_Mega_Menu__c'] is not None:
        is_mega = True
    if 'Collection__r' in o and o['Collection__r'] is not None and o['Collection__r']['CMS_Mega_Menu__c'] is not None:
        is_mega = True
    values = [oname, id, 'https://deltadentalwi--coredx.lightning.force.com/lightning/r/' + oname + '/' + id + '/view', is_mega, field, '', label, value, options]
    print(values)
    csv.writerow(values)

def write_mega(csv,o, oname, id, field,label, value):
    values = [oname, id, 'https://deltadentalwi--coredx.lightning.force.com/lightning/r/' + oname + '/' + id + '/view', True, field, '', label, value]
    print(values)
    csv.writerow(values)

def breakdown(sf):
    f = csv.writer(open('body_content_backup' + str(datetime.datetime.now()) + '.csv', 'w'))

    for row in sf.query_all('select Id, body__c from CMS_Content__c')['records']:
        if row['Body__c']:
            print(row)
            f.writerow([row['Id'], 'Body__c', row['Body__c']])

    for row in sf.query_all('select Id, breadcrumb__c,Broker_Breadcrumb__c,slug__c, Employer_Breadcrumb__c,Provider_Breadcrumb__c, Member_Mobile_breadcrumb__c,Broker_Mobile_Breadcrumb__c,Employer_Mobile_Breadcrumb__c,Provider_Mobile_Breadcrumb__c from CMS_Page__c')['records']:
        if row['breadcrumb__c']: f.writerow([row['Id'], 'breadcrumb__c', row['breadcrumb__c']])
        if row['Broker_Breadcrumb__c']: f.writerow([row['Id'], 'Broker_Breadcrumb__c', row['Broker_Breadcrumb__c']])
        if row['Employer_Breadcrumb__c']: f.writerow([row['Id'], 'Employer_Breadcrumb__c', row['Employer_Breadcrumb__c']])
        if row['Provider_Breadcrumb__c']: f.writerow([row['Id'], 'Provider_Breadcrumb__c', row['Provider_Breadcrumb__c']])
        if row['Member_Mobile_Breadcrumb__c']: f.writerow([row['Id'], 'Member_Mobile_Breadcrumb__c', row['Member_Mobile_Breadcrumb__c']])
        if row['Broker_Mobile_Breadcrumb__c']: f.writerow([row['Id'], 'Broker_Mobile_Breadcrumb__c', row['Broker_Mobile_Breadcrumb__c']])
        if row['Employer_Mobile_Breadcrumb__c']: f.writerow([row['Id'], 'Employer_Mobile_Breadcrumb__c', row['Employer_Mobile_Breadcrumb__c']])
        if row['Provider_Mobile_Breadcrumb__c']: f.writerow([row['Id'], 'Provider_Mobile_Breadcrumb__c', row['Provider_Mobile_Breadcrumb__c']])

    f = csv.writer(open('links.csv','w'))
    f.writerow(['Object','ID', 'Link', 'Mega Menu', 'Field','Coordinates','Label', 'href'])
    fields = '''Link_Options__c, Id, slug__c, Title__c, RecordType.Name, Name, body__c, link__c, link_text__c, CMS_Mega_Menu__c, Collection__r.CMS_Mega_Menu__c '''
    for content in sf.query_all('select ' + fields + ' ,(select ' + fields + ' from Contents__r) from CMS_Content__c')['records']:
        if content['Body__c']:
            for m in re.finditer('\[(.*?)\]\((.*?)\)', content['Body__c']):
                write_match(f, content, 'CMS_Content__c', content['Id'], 'Body__c', m)
            for m in re.finditer('href="(.*?)"', content['Body__c']):
                write_match(f, content, 'CMS_Content__c', content['Id'], 'Body__c', m)
            if(content['Link_Text__c']):
                write_link(f, content, 'CMS_Content__c',content['Id'], 'link__c', content['Link_Text__c'], content['link__c'], content['Link_Options__c'])
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
                    write_link(f, child, 'CMS_Content__c',child['Id'], 'Link__c', child['Link_Text__c'], child['link__c'], child['Link_Options__c'])
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


def update(sf, page, field):
    if page[field]:
        record = page[field]
        record = record.replace('[Home](home)','[Home](..)')
        record = record.replace('[Home](Home)','[Home](..)')
        record = record.replace('[Home](#)','[Home](..)')
        record = record.replace('[home](home)','[Home](..)')
        record = record.replace('[Home](member-page)','[Home](..)')

        record = record.replace(')>[',') > [')
        record = record.replace('[Our Company](#)','[Our Company](our-company)')
        record = record.replace('[Careers](#)','[Careers](careers)')
        record = record.replace('[Online Tools](Online Tools)','[Online Tools](online-tools)')
        print(record)
        sf.CMS_Page__c.update(page['Id'], {field:record})



def load(sf, args):
    for page in sf.query_all('select Id, breadcrumb__c,Broker_Breadcrumb__c,slug__c, Employer_Breadcrumb__c,Provider_Breadcrumb__c, Member_Mobile_breadcrumb__c,Broker_Mobile_Breadcrumb__c,Employer_Mobile_Breadcrumb__c,Provider_Mobile_Breadcrumb__c from CMS_Page__c')['records']:
        update(sf, page, 'breadcrumb__c')
        update(sf, page, 'Broker_Breadcrumb__c')
        update(sf, page, 'Employer_Breadcrumb__c')
        update(sf, page, 'Provider_Breadcrumb__c')
        update(sf, page, 'Member_Mobile_Breadcrumb__c')
        update(sf, page, 'Broker_Mobile_Breadcrumb__c')
        update(sf, page, 'Employer_Mobile_Breadcrumb__c')
        update(sf, page, 'Provider_Mobile_Breadcrumb__c')






sf = Salesforce(username=args.username, password=args.password, sandbox=args.sandbox, security_token=args.token)

if args.action == 'breakdown':
    breakdown(sf)
if args.action == 'load':
    load(sf, args)
