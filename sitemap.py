import sys
if sys.version_info < (3, 0):
    sys.stdout.write("Sorry, this software requires Python 3(.7), not Python " + str(sys.version_info.major) + '.' +  str(sys.version_info.minor) + "\n")
    sys.exit(1)

import _lib
import datetime
from simple_salesforce import Salesforce

import argparse
from yattag import Doc
from bs4 import BeautifulSoup


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

def convert_breadcrumb(crumb):
    rs = {'children':{}}
    rs['Name'] = crumb[crumb.index('[') + 1 : crumb.index(']')]
    rs['uri__c'] = get_key(crumb.strip()[crumb.index('('):-1].lower())
    return rs

def get_key(value):
    return str(value).lower().replace(' ','-')

def sitemap(sf):
    map = {'Members':{}, 'Brokers':{}, 'Employers':{}, 'Providers': {}}

    for page in sf.query('select Name, breadcrumb__c, Broker_Breadcrumb__c, Employer_Breadcrumb__c, Provider_Breadcrumb__c, uri__c from CMS_Page__c')['records']:
        member_bread = page['breadcrumb__c']
        page['children'] = {}
        for persona in map.keys():
            if member_bread is None:
                map[persona][get_key(page['uri__c'])] = page
            else:
                levels = member_bread.split('>')
                if len(levels) == 1:
                    if get_key(page['uri__c']) in map[persona]:
                        continue
                    map[persona][get_key(page['uri__c'])] = page
                elif len(levels) == 2:
                    parent = convert_breadcrumb(levels[1])
                    if get_key(parent['uri__c']) not in map[persona]:
                        map[persona][get_key(parent['uri__c'])] = parent
                    map[persona][get_key(parent['uri__c'])]['children'][get_key(page['uri__c'])] = page
                elif len(levels) == 3:
                    parent = convert_breadcrumb(levels[1])
                    if get_key(parent['uri__c']) not in map[persona]:
                        map[persona][get_key(parent['uri__c'])] = parent
                    child = convert_breadcrumb(levels[2])
                    if get_key(child['uri__c']) not in map[persona][get_key(parent['uri__c'])]['children']:
                        map[persona][get_key(parent['uri__c'])]['children'][get_key(child['uri__c'])] = child
                    map[persona][get_key(parent['uri__c'])]['children'][get_key(child['uri__c'])]['children'][get_key(page['uri__c'])] = page




    doc, tag, text = Doc().tagtext()
    for k in map.keys():
        with tag('a', href='../?persona=' + k[:-1]):
            with tag('span'):
                text(k)
        with tag('ul'):
            for p1 in map[k].keys():
                with tag('li'):
                    with tag('a', href= str(p1) + '?persona=' + k[:-1]):
                        with tag('span'):
                            text(map[k][p1]['Name'])
                if len(map[k][p1]['children']) > 0:
                    with tag('ul'):
                        for p2 in map[k][p1]['children'].keys():
                            with tag('li'):
                                with tag('a', href= str(p2) + '?persona=' + k[:-1]):
                                    with tag('span'):
                                        text(map[k][p1]['children'][p2]['Name'])
                            if len(map[k][p1]['children'][p2]['children']) > 0:
                                with tag('ul'):
                                    for p3 in map[k][p1]['children'][p2]['children'].keys():
                                        with tag('li'):
                                            with tag('a', href= str(p3) + '?persona=' + k[:-1]):
                                                with tag('span'):
                                                    text(map[k][p1]['children'][p2]['children'][p3]['Name'])



    print(BeautifulSoup(doc.getvalue(), 'html.parser').prettify())






sf = Salesforce(username=args.username, password=args.password, sandbox=args.sandbox, security_token=args.token)
sitemap(sf)

