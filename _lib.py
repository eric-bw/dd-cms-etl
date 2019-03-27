from openpyxl import load_workbook, Workbook
import datetime
import base64
import requests
import csv
import os
import shutil
import zipfile

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")

class Transfer:
    def __init__(self):
        self.a = None
        self.b = None
        self.a_id = None
        self.b_id = None

def create_pages(sf):
    wb = load_workbook('input/site.xlsx')
    for sheet_name in wb.sheetnames:
        if sheet_name == 'pages':
            sheet = wb[sheet_name]
            for i, row in enumerate(sheet.rows):
                if i > 0:
                    q = 'select id from CMS_Page__c where uri__c = \'%s\''%(row[3].value,)
                    rs = sf.query(q)['records']
                    if rs:
                        sheet[row[0].coordinate] = rs[0]['Id']
                    else:
                        record = sf.CMS_Page__c.create({'Name':row[1].value,
                                                        'breadcrumb__c':row[2].value,
                                                        'Story__c': row[3].value,
                                                        'uri__c': row[4].value})
                        sheet[row[0].coordinate] = record['id']
    wb.save('input/site.xlsx')

def output(sf, filepath) :
    wb = Workbook()
    wb.remove_sheet(wb.active)
    add_sheet(sf, wb, ['Id'], 'CMS_Mega_Menu__c', 'Mega Menu')
    add_sheet(sf, wb, ['Id'], 'CMS_Page__c', 'Pages')
    add_sheet(sf, wb, ['Id','Name'], 'CMS_Collection__c', 'Collections')
    add_sheet(sf, wb, ['Id','Name'], 'CMS_Content__c', 'Contents')
    add_sheet(sf, wb, ['Id'],'CMS_Asset__c', 'Assets')
    add_sheet_content(sf, wb, ['Id','ContentSize','Checksum'], 'ContentVersion', 'Files', filepath)
    wb.save(filepath + '.xlsx')

    zipf = zipfile.ZipFile(filepath + '.zip', 'w')
    zipf.write(filepath + '.xlsx')
    for f in os.listdir('./content'):
        zipf.write('./content/' + f)
    os.remove(filepath + '.xlsx')
    shutil.rmtree('./content')


def add_sheet(sf, wb, fields,  object_name, sheet_name):
    meta = sf.__getattr__(object_name).describe()
    records = sf.query('select ' + ','.join(fields) +','+ ','.join([x['name'] for x in meta['fields'] if x['createable']]) + ' from ' + object_name + ' order by createddate')['records']
    wb.create_sheet(sheet_name)
    sheet = wb[sheet_name]
    for i, row in enumerate(records):
        if i == 0:
            th = [x for x in row.keys() if x not in ['attributes','OwnerId']]
            sheet.append(th)
        tr = [y for x,y in row.items() if x not in ['attributes','OwnerId']]


        sheet.append(tr)

def add_sheet_content(sf, wb, fields,  object_name, sheet_name, filepath):
    meta = sf.__getattr__(object_name).describe()
    records = sf.query('select ' + ','.join(fields) +','+ ','.join([x['name'] for x in meta['fields'] if x['createable']]) +
                       ' from ' + object_name +
                       ' where ContentDocumentId in (\'' + '\',\''.join(get_file_list(sf)) +'\') ' +
                       ' order by createddate')['records']
    wb.create_sheet(sheet_name)
    sheet = wb[sheet_name]
    if os.path.exists('./content'):
        shutil.rmtree('./content')
    os.mkdir('./content')
    for i, row in enumerate(records):
        if i == 0:
            th = [x for x in row.keys() if x not in ['attributes','OwnerId']]
            sheet.append(th)
        tr = [y for x,y in row.items() if x not in ['attributes','OwnerId']]

        url = "https://%s%s" % (sf.sf_instance, row['VersionData'])
        response = requests.get(url, headers={"Authorization": "OAuth " + sf.session_id, "Content-Type": "application/octet-stream"})
        if response.ok:
            byte_string = str(base64.b64encode(response.content))
            byte_string = byte_string[2:-1]
            with open('./content' + '/' + row['ContentDocumentId'],'w') as f:
                f.write(byte_string)
                f.close()
        else:
            print('file err: ' + response)
            open('./content' + '/' + row['ContentDocumentId'],'w')


        sheet.append(tr)

def get_data(sheet, key='Id'):
    rs = {}
    field_map = {}
    for i, row in enumerate(sheet.rows):
        if i == 0:
            for n, f in enumerate(row):
                field_map[n] = f.value
        else:
            data = {}
            id = None
            for n, f in enumerate(row):
                header = field_map[n]
                if header == key:
                    id = f.value
                    continue
                data[header] = f.value
            t = Transfer()
            t.a = data
            t.a_id = id
            rs[id] = t
    return rs

def transfer_pages(map, wb, wb_out, sf, read_only=False):
    sheet_name = 'Pages'
    sheet = wb[sheet_name]
    data = get_data(sheet, 'Id')



    for row in data.values():
        note = ''
        record = row.a.copy()
        exists = sf.query('select id, Name from CMS_Page__c where Name = \'%s\''%(row.a['Name']))['records']
        if exists:
            row.b_id = exists[0]['Id']
            row.b = exists[0]
            if not read_only: sf.CMS_Page__c.update(row.b_id, record)
            note += 'updated %s;'%row.b_id
        else:
            if not read_only:
                rs = sf.CMS_Page__c.create(row.a)
                row.b_id = rs['id']
                row.b = row.a
                note += 'created record ' + row.b_id + ';'
            else:
                raise Exception('record does not exist' + record['Name'])
        record['Id'] = row.b_id
        wb_out.writerow([row.a_id,row.b_id, note])
    map.update(data)

def convert(filepath, sf, wb_out):
    archive = zipfile.ZipFile(filepath, 'r')
    for x in archive.namelist():
        if x.endswith('.xlsx'):
            excel_file = archive.open(x)
            break

    wb = load_workbook(excel_file)

    wb_out.writerow(['ORIGINAL_ID','NEW_ID','Notes'])
    map = {}


    transfer_pages(map, wb, wb_out,  sf, True)

    sheet_name = 'Collections'
    sheet = wb[sheet_name]
    data = get_data(sheet)

    recordtype = get_recordtype(sf.CMS_Content__c.describe(), 'Collection')

    for row in data.values():
        note = ''
        record = row.a.copy()
        if record['CMS_Page__c'] in map:
            record['CMS_Page__c'] = map[row.a['CMS_Page__c']].b_id
        record['RecordTypeId'] = recordtype['recordTypeId']
        exists = sf.query('select id, Name from CMS_Content__c where name = \'%s\' or slug__c = \'%s\''%(row.a['Name'], row.a['Slug__c']))['records']
        if exists:
            row.b_id = exists[0]['Id']
            row.b = exists[0]
            sf.CMS_Content__c.update(row.b_id, record)
            note += 'updated %s;'%row.b_id
        else:
            rs = sf.CMS_Content__c.create(record)
            row.b_id = rs['id']
            row.b = row.a
            note += 'created record ' + row.b_id + ';'
            record['Id'] = row.b_id
            wb_out.writerow([row.a_id,row.b_id, note])
    map.update(data)

    transfer(filepath, sf, wb_out, map)

def get_recordtype(meta, recordtype_name):
    for rt in meta['recordTypeInfos']:
        if rt['name'] == recordtype_name:
            return rt
    return None

def transfer_content(map, wb, wb_out, sf, read_only=False):
    sheet_name = 'Contents'
    sheet = wb[sheet_name]
    data = get_data(sheet)

    for row in data.values():
        note = ''
        record = row.a.copy()
        if 'CMS_Collection__c' in record and record['CMS_Collection__c'] in map:
            record['Collection__c'] = map[record['CMS_Collection__c']].b_id

        if record['CMS_Page__c'] in map:
            record['CMS_Page__c'] = map[record['CMS_Page__c']].b_id

        exists = sf.query('select id, Name from CMS_Content__c where name = \'%s\' or slug__c = \'%s\''%(row.a['Name'], row.a['Slug__c']))['records']

        if 'CMS_Collection__c' in record:
            record.pop('CMS_Collection__c')

        if exists:
            row.b_id = exists[0]['Id']
            row.b = exists[0]
            if not read_only: sf.CMS_Content__c.update(row.b_id, record)
            note += 'updated %s;'%row.b_id
        else:
            if not read_only:
                rs = sf.CMS_Content__c.create(record)
                row.b_id = rs['id']
                row.b = row.a
                note += 'created record ' + row.b_id + ';'
            else:
                raise Exception('record does not exist' + record['Name'])
        record['Id'] = row.b_id
        wb_out.writerow([row.a_id,row.b_id, note])
    map.update(data)

def transfer_files(map, wb, wb_out, sf, archive, read_only=False):
    sheet_name = 'Files'
    sheet = wb[sheet_name]
    data = get_data(sheet, 'ContentDocumentId')

    for document_id, row in data.items():
        note = ''
        record = row.a.copy()
        exists = sf.query('select id, Title, VersionData, PathOnClient, ContentDocumentId from ContentVersion where PathOnClient = \'%s\''%(row.a['PathOnClient']))['records']
        if exists:
            row.b_id = exists[0]['Id']
            row.b = exists[0]
            note += 'record exists %s, no update;'%row.b_id
        else:
            if not read_only:
                b64encoded = archive.read('content/' + document_id).decode('utf-8')
                row.b = {'title' : row.a['Title'],'PathOnClient' : row.a['PathOnClient'],'VersionData' : b64encoded}
                content = sf.ContentVersion.create(row.b)
                row.b_id = content['id']
                row.b = sf.query('select id, Title, VersionData, PathOnClient, ContentDocumentId from ContentVersion where id = \'%s\''%(row.b_id))['records'][0]
                note += 'created record ' + row.b_id + ';'
            else:
                raise Exception('record does not exist' + record['Title'])
        record['Id'] = row.b_id
        wb_out.writerow([row.a_id,row.b_id, note])
    map.update(data)

def get_file_list(sf):
    rs = []
    for row in sf.query('select ContentDocument__c from CMS_Asset__c')['records']:
        rs.append(row['ContentDocument__c'])
    return rs

def transfer_assets(map, wb, wb_out, sf):
    sheet_name = 'Assets'
    sheet = wb[sheet_name]
    data = get_data(sheet)


    for row in data.values():
        note = ''
        record = row.a.copy()

        if record['CMS_Content__c'] in map:
            record['CMS_Content__c'] = map[record['CMS_Content__c']].b_id
        else:
            note += 'record missing content %s;'%(record['CMS_Content__c'])

        if row.a['ContentDocument__c'] in map:
            record['ContentDocument__c'] = map[row.a['ContentDocument__c']].b['ContentDocumentId']
            record['ContentVersion__c'] = map[row.a['ContentDocument__c']].b['Id']
        else:
            note += 'record %s missing version;'%(record['ContentVersion__c'])


        #TODO: remove temporary mapping translation
        record['File_Type__c'] = record['type__c']
        record['Type__c'] = record['Name']
        if 'Name' in record:
            record.pop('Name')

        exists = sf.query('select id, Name from CMS_Asset__c where name = \'%s\' and CMS_Content__c = \'%s\''%(row.a['Name'], record['CMS_Content__c']))['records']
        if exists:
            row.b_id = exists[0]['Id']
            row.b = exists[0]
            try:
                rs = sf.CMS_Asset__c.update(row.b_id, record)
                note += 'updated %s;'%row.b_id
            except Exception as e:
                note += 'updated failed %s -- %s;'%(row.b_id, e.content[0]['message'])
        else:
            rs = sf.CMS_Asset__c.create(record)
            row.b_id = rs['id']
            row.b = row.a
            note += 'created record ' + row.b_id + ';'
        row.a['Id'] = row.b_id
        wb_out.writerow([row.a_id,row.b_id, note])
    map.update(data)

def transfer(filepath, sf, wb_out, map={}, read_only = False):
    archive = zipfile.ZipFile(filepath, 'r')
    excel_file = None
    for x in archive.namelist():
        if x.endswith('.xlsx'):
            excel_file = archive.open(x)
            break

    if excel_file is None:
        raise Exception('file not found')

    wb = load_workbook(excel_file)
    print('transferring files')
    transfer_files(map, wb, wb_out, sf, archive, read_only)
    print('transferring pages')
    transfer_pages(map, wb, wb_out,  sf, read_only)
    print('transferring content')
    transfer_content(map, wb, wb_out, sf, read_only)
    print('transferring assets')
    transfer_assets(map, wb, wb_out, sf)
    print('done')

def clear_content(sf):
    print('clearing existing data')
    for o in ['CMS_Mega_Menu__c','CMS_Page__c','CMS_Collection__c','CMS_Content__c']:
        try:
            print('deleting ' + o)
            for row in sf.query('select id from ' + o)['records']:
                sf.__getattr__(o).delete(row['Id'])
                print('.', end='')
        except:
            print('err, skipping ' + o)
    print('done')