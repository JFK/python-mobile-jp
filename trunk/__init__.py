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

import re

class factory:

    def __init__(self, **kwargs):
    
        if re.compile(r'^DoCoMo/\d\.\d[ /]').match(kwargs['userAgent']):
            self.cls = __import__(kwargs['libName'] + '.docomo').mobile.docomo.factory()
    
        elif re.compile(r'^(?:KDDI-[A-Z]+\d+[A-Z]? )?UP\.Browser\/').match(kwargs['userAgent']):
            self.cls = __import__(kwargs['libName'] + '.au').mobile.au.factory()
    
        elif re.compile(r'^(?:(?:SoftBank|Vodafone)/\d\.\d|MOT-)').match(kwargs['userAgent']):
            self.cls = __import__(kwargs['libName'] + '.softbank').mobile.softbank.factory()
    
        else:
            self.cls =  __import__(kwargs['libName'] + '.pc').mobile.pc.factory()

        self.imageUrl = kwargs['imageUrl']
        self.carrierType = self.cls.type()

        if self.carrierType == 'pc' or self.carrierType == 'softbank':
            self.charset = 'UTF-8'
        else:
            self.charset = 'Shift_JIS'

    def to_unicode(self, text):
        for x in self.cls.find(text):
            text = text.replace(x.encode('UTF-8'), self._decode(x.encode('UTF-8')))
        return unicode(text, 'UTF-8')

    def echo(self, text):
        for x in re.findall(ur'([\ue000-\uf8ff])', text, re.UNICODE):
            text = text.replace(x, self._encode(x))
        return text

    def _decode(self, text):
        if not text: return
        for x in self.cls.map():
            if x[1] == text:
                return x[0]
        return text

    def _encode(self, text):
        if not text: return
        for x in self.cls.map():
            if x[0] == text.encode('UTF-8'):
                if self.carrierType == 'pc':
                    return "<img src='%s%s.gif' />" % \
                        (self.imageUrl, ''.join(map(lambda x: "%02x" % ord(x), x[1])))
                return unicode(x[1],'UTF-8')
        return text

