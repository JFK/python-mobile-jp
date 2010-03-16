#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

import re

class factory:
    def __init__(self, **kwargs):

        libName = kwargs['libName']
        userAgent = kwargs['userAgent']

        DOCOMO_RE   = re.compile(r'^DoCoMo/\d\.\d[ /]')
        SOFTBANK_RE = re.compile(r'^(?:(?:SoftBank|Vodafone)/\d\.\d|MOT-)')
        AU_RE = re.compile(r'^(?:KDDI-[A-Z]+\d+[A-Z]? )?UP\.Browser\/')

        if DOCOMO_RE.match(userAgent):
            __import__(libName + '.docomo')
            self.carrier = convert(docomo.factory())

        elif AU_RE.match(userAgent):
            __import__(libName + '.au')
            self.carrier = convert(au.factory())

        elif SOFTBANK_RE.match(userAgent):
            __import__(libName + '.softbank')
            self.carrier = convert(softbank.factory())

        else:
            __import__(libName + '.pc')
            self.carrier = convert(
                pc.factory(),
                imageUrl = kwargs['imageUrl']
                )

class convert:
    def __init__(self, cls, imageUrl=''):
        self._ = cls
        self.dict = {}
        self.dict.update({'imageUrl':imageUrl})
        self.dict.update({'carrierType':cls.type()})
        if self.carrierType == 'pc' or self.carrierType == 'softbank':
            self.dict.update({'charset':'UTF-8'})
        else:
            self.dict.update({'charset':'Shift_JIS'})

    def __getattr__(self, key):
        return self.dict[key]

    def decode_all(self, text):
        print map(hex,map(ord, text))
        for x in self._.find(text):
            text = text.replace(x.encode('UTF-8'), self.decode(x.encode('UTF-8')))
        return text

    def decode(self, text):
        if not text: return
        for x in self._.map():
            if x[1] == text:
                return x[0]
        return text

    def encode_all(self, text):
        for x in re.findall(ur'([\ue000-\uf8ff])', text, re.UNICODE):
            try:
                text = text.replace(x, self.encode(x))
            except UnicodeDecodeError, e: pass
        return text

    def encode(self, text):
        if not text: return
        for x in self._.map():
            if x[0] == text.encode('UTF-8'):
                if self.carrierType == 'pc':
                    return "<img src='%s%s.gif' />" % \
                        (self.imageUrl, ''.join(map(lambda x: "%02x" % ord(x), x[1])))
                try:
                    return unicode(x[1],'UTF-8')
                except TypeError, e: pass
        return text
