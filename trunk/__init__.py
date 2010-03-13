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

        libName = kwargs['libName']
        userAgent = kwargs['userAgent']

        DOCOMO_RE   = re.compile(r'^DoCoMo/\d\.\d[ /]')
        SOFTBANK_RE = re.compile(r'^(?:(?:SoftBank|Vodafone)/\d\.\d|MOT-)')
        AU_RE = re.compile(r'^(?:KDDI-[A-Z]+\d+[A-Z]? )?UP\.Browser\/')

        if DOCOMO_RE.match(userAgent):
            __import__(libName + '.docomo')
            self.carrier = convert(
                translationTable = docomo.map(),
                carrierType = 'docomo'
                )

        elif AU_RE.match(userAgent):
            __import__(libName + '.au')
            self.carrier = convert(
                translationTable = au.map(),
                carrierType = 'au'
                )

        elif SOFTBANK_RE.match(userAgent):
            __import__(libName + '.softbank')
            self.carrier = convert(
                translationTable = softbank.map(),
                carrierType = 'softbank'
                )

        else:
            __import__(libName + '.pc')
            self.carrier = convert(
                translationTable = pc.map(),
                carrierType = 'pc',
                imageUrl = kwargs['imageUrl']
                )

class convert:
    def __init__(self, **kwargs):
        self.dict = {}
        self.dict.update(kwargs)

    def emoji(self, text):
        for x in self.dict['translationTable']:
            if x[0] == text:
                text = b""+x[1]+""
                break

        if self.dict['carrierType'] == 'pc':
            return "<img src='%s%s.gif' />" % \
                (self.dict['imageUrl'], ''.join(map(lambda x: "%02x" % ord(x), text)))

        elif self.isUtf8Carrier():
            return text
        else:
            return ''.join(map(lambda x: "&#x%02x;" % ord(x), unicode(text, 'UTF-8')))

    def echo(self, text):
        if self.isUtf8Carrier():
            return text
        return unicode(text,'utf-8').encode('Shift_JIS')

    def charset(self):
        if self.isUtf8Carrier():
            return 'UTF-8'
        return 'Shift_JIS'

    def isUtf8Carrier(self):
        if self.dict['carrierType'] == 'pc' or self.dict['carrierType'] == 'softbank':
            return True;
        return False;
