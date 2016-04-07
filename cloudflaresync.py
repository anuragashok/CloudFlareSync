__author__ = 'anurag'

import csv
import sys
import json
import argparse
import os

import requests


class CFAPIException(Exception):
    def __init__(self, message):
        self.message = message


class CFAPI:
    'Utiliy Class to get data from CloudFlare API'

    def __init__(self, tkn, email, url):
        self.tkn = tkn
        self.email = email
        self.url = url

    def call(self, data):
        data['tkn'] = self.tkn
        data['email'] = self.email
        response = requests.get(self.url, params=data)
        if (response.status_code != requests.codes.ok):
            raise CFAPIException("CFAPI got a {status} error while calling the CloudFlare API at {url}".format(
                status=response.status_code, url=self.url))
        response = response.json()
        if (response['result'] == 'error'):
            raise CFAPIException(response['msg'])
        if (response.get('response')):
            return response['response']
        else:
            return None

    def zone_load_multi(self):
        data = dict()
        data['a'] = 'zone_load_multi'
        result = self.call(data)
        return result['zones']

    def rec_load_all(self, zone):
        data = dict()
        data['a'] = 'rec_load_all'
        data['z'] = zone
        result = self.call(data)
        if (result['recs'].get('objs')):
            return result['recs']['objs']
        else:
            return list()

    def rec_new(self, rec):
        data = dict()
        data['a'] = 'rec_new'
        data['z'] = rec['zone_name']
        rec['zone_name'] = None
        for k, v in rec.items():
            if v is not None:
                data[k] = v
        result = self.call(data)
        return result

    def rec_edit(self, rec):
        data = dict()
        data['a'] = 'rec_edit'
        data['z'] = rec['zone_name']
        rec['zone_name'] = None
        data['id'] = rec['rec_id']
        rec['rec_id'] = None
        for k, v in rec.items():
            if v is not None:
                data[k] = v
        result = self.call(data)
        return result

    def rec_delete(self, rec):
        data = dict()
        data['a'] = 'rec_delete'
        data['z'] = rec['zone_name']
        rec['zone_name'] = None
        data['id'] = rec['rec_id']

        for k, v in rec.items():
            if v is not None:
                data[k] = v
        result = self.call(data)
        return result


class CFSync:
    def __init__(self, cfapi, file, fieldnames, localData, domains, backup_file):
        self.cfapi = cfapi
        self.remoteData = dict()
        self.localData = localData
        self.file = file
        self.fieldnames = fieldnames
        self.domains = domains
        self.backup_file = backup_file

    def setLocalData(self, localData):
        self.localData = localData

    def fetchRemoteData(self):
        self.zoneList = list()
        zones = self.cfapi.zone_load_multi()
        for zone in zones['objs']:

            if (zone['zone_name'] in self.domains):
                print(zone['zone_name'])
                self.zoneList.append(zone['zone_name'])

        self.remoteData = list()
        for zone_name in self.zoneList:
            objs = self.cfapi.rec_load_all(zone_name)
            for rec in objs:
                row = dict()
                row['zone_name'] = rec.get('zone_name')
                row['type'] = rec.get('type')
                row['name'] = rec.get('name')
                row['content'] = rec.get('content')
                row['ttl'] = rec.get('ttl')
                row['service_mode'] = rec.get('service_mode')
                row['prlo'] = rec.get('prlo')
                row['service'] = rec.get('service')
                row['srvname'] = rec.get('srvname')
                row['protocol'] = rec.get('protocol')
                row['weight'] = rec.get('weight')
                row['port'] = rec.get('port')
                row['target'] = rec.get('target')
                row['rec_id'] = rec.get('rec_id')
                self.remoteData.append(row)

    def writeRecordsToFile(self, file, data):
        writer = csv.DictWriter(f=open(file, 'w'), fieldnames=self.fieldnames)
        writer.writeheader()
        writer.writerows(data)

    def sync(self):
        self.fetchRemoteData()

        self.writeRecordsToFile('cf_before_sync.csv', self.remoteData)

        add = list()
        edit = list()
        delete = list()

        for rec in self.localData:
            if (rec.get('rec_id') is None):
                add.append(rec)
            else:
                for rec2 in self.remoteData:
                    if (rec2.get('rec_id') == rec.get('rec_id')):
                        if (rec != rec2):
                            edit.append(rec)

        for rec2 in self.remoteData:
            deleteFlag = True
            for rec in self.localData:
                if (rec2.get('rec_id') == rec.get('rec_id')):
                    deleteFlag = False
                    break
            if (deleteFlag):
                delete.append(rec2)

        self.localData[:] = [d for d in self.localData if d.get('rec_id') is None]

        cfadded = list()
        if len(add) > 0:
            for rec in add:
                cfapi.rec_new(rec)
        if len(edit) > 0:
            for rec in edit:
                cfapi.rec_edit(rec)
        if len(delete) > 0:
            for rec in delete:
                cfapi.rec_delete(rec)


    def fetch(self):
        self.fetchRemoteData()

        self.writeRecordsToFile(self.file, self.remoteData)


file = ''
records = dict()
try:
    #Read settings from config.json
    if (os.path.isfile('config.json') == False):
        sys.exit('Please ensure that you have renamed config.default.json to config.json')
    with open('config.json', 'r') as f:
        config = json.load(f)

    file = config['file']
    backup_file = config['backup_file']
    domains = config['domains']

    cfapi = CFAPI(config['tkn'], config['email'], config['url'])

    parser = argparse.ArgumentParser()
    parser.add_argument('-fetch', action='store_true', help='Fetch data from cloudflare')
    parser.add_argument('-sync', action='store_true', help='Sync local data to cloudflare')
    args = parser.parse_args()

    if not (args.fetch or args.sync):
        parser.error('No action requested, add -fetch or -sync')

    records = csv.DictReader(open(file, newline=''), delimiter=',', quotechar='"')
    localData = list()
    fulllocaldata = list()
    for rec in records:
        for k, v in rec.items():
            if v is '':
                rec[k] = None
        if (rec.get('rec_id') != None):
            fulllocaldata.append(rec)
        if (rec.get('zone_name') in domains):
            localData.append(rec)
    cfsync = CFSync(cfapi, file, records.fieldnames, localData, domains, backup_file)
    if (args.sync):
        cfsync.sync()
    if (args.fetch):
        cfsync.fetch()

except csv.Error as e:
    sys.exit('file %s, line %d: %s' % (file, records.line_num, e))

except CFAPIException as e:
    sys.exit(e.message)

except Exception as e:
    sys.exit(e)




