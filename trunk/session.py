#!/usr/bin/env python
#
# Copyright 2010 fumikazu.kiyota@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import string
import random
import time
import base64
import hashlib
import urllib
from pymongo import Connection, ASCENDING

class start:

    def __init__(self, **kwargs):
        self.authdb = 'sessiondb.transaction' if 'sessiondb' not in kwargs else kwargs['sessiondb']
        self.keyname = '_tk' if 'keyname' not in kwargs else kwargs['keyname']
        self.keylength = 128 if 'keylength' not in kwargs else kwargs['keylength']
        self.lifetime = 31 * 86400 if 'lifetime' not in kwargs else kwargs['lifetime']
        self.session = None

        con = Connection()
        self._con = eval('con.' + self.authdb)
        self._gc()

    def _token(self):
        letters=string.ascii_letters+string.digits
        rnd = ''.join([random.choice(letters) for _ in range(self.keylength)])
        return base64.b64encode(''.join([str(int(time.time())),rnd]))

    def _gc(self):
        self._con.remove({'time':{'$gt':time.time() - self.lifetime}})

    def remove(self):
        self._con.remove({'key':self.key()})

    def save(self, data):
        self._con.update({"key":self.key()},
            {'$set': {'data':data,'time':str(int(time.time()))}})

    def data(self):
        return self._con.find_one({"key":self.key()})['data']

    def lock(self, key):
        token = self._token()
        self._con.remove({'key':key})
        self._con.insert({'key':key,'token':token,'time':str(int(time.time()))})
        self._con.create_index([("key", ASCENDING)])
        self.session = "|".join([base64.b64encode(key),token])

    def open(self, value, **kwargs):
        if not value: return None
        parts = value.split("|")
        if len(parts) != 2: return None
        key = base64.b64decode(parts[0])
        result = self._con.find_one({"key":key})
        if result and 'token' in result and result['token'] == parts[1] \
             and result['time'] >= time.time() - self.lifetime:
            if 'renew' in  kwargs and kwargs['renew']:
                token = self._token()
                self._con.update({"key":key},
                    {'$set': {'token':token,'time':str(int(time.time()))}})
                self.session = "|".join([parts[0], token])
            else:
                self._con.update({"key":key},
                    {'$set': {'time':str(int(time.time()))}})
                self.session = "|".join([parts[0], parts[1]])
            return True
        else:
            self._con.remove({'key':key})
            return False

    def key(self):
        if not self.session: return None
        parts = self.session.split("|")
        if len(parts) != 2: return None
        return base64.b64decode(parts[0])

    def urlencode(self):
        return urllib.urlencode({self.keyname:self.session})

    def form_html(self):
        return '<input type="hidden" name="' + self.keyname + '" value="' + self.session + '"/>'
