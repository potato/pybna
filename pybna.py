#!/usr/bin/env python2

# This file is part of pybna.
#
# pybna is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pybna is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with pybna. If not, see <http://www.gnu.org/licenses/>.
#
# (C) 2012- by Laszlo Hammerl, <mail@crazypotato.tk>

import random
import ctypes
import urllib2
import time
import hmac
import hashlib
import struct
import csv
import os
from optparse import OptionParser

TOKEN_FILE = './tokens.csv'

RSA_KEY = 257
PUB_KEY = 104890018807986556874007710914205443157030159668034197186125678960287470894290830530618284943118405110896322835449099433232093151168250152146023319326491587651685252774820340995950744075665455681760652136576493028733914892166700899109836291180881063097461175643998356321993663868233366705340758102567742483097
M_URL = 'http://m.%s.mobileservice.blizzard.com'
M_ENROLL = '/enrollment/enroll.htm'
M_SYNC   = '/enrollment/time.htm'

class Token(object):
    def __init__(self, region = 'eu'):
        self.secret = ''
        self.serial = ''
        self.region = region.upper()
        self.offset = 0

    def generate(self):
        while True:
            otp = ''.join(chr(random.randint(0, 255)) for i in range(37))
            msg = '%d%s%s%s' % (1, otp, self.region, 'Motorola RAZR v3')
            n = pow(int(msg.encode('hex'), 16), RSA_KEY, PUB_KEY)
            a = ctypes.create_string_buffer(n.bit_length() // 8 + 1)
            pyba = ctypes.pythonapi._PyLong_AsByteArray
            pyba.argtypes = [ctypes.py_object, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_int, ctypes.c_int]
            pyba(n, a, len(a), 0, 1)
            req = urllib2.Request(M_URL % self.region + M_ENROLL)
            req.add_header('Content-type', 'application/octet-stream')
            req.add_header('Content-length', len(a.raw))
            req.add_data(a.raw)
            res = bytearray(urllib2.urlopen(req).read())
            for i in range(37):
                res[i+8] ^= ord(otp[i])
            if str(res[28:31]) == '%s-' % (self.region):
                self.serial = str(res[28:])
                self.secret = ''.join(['%02X' % c for c in res[8:28]])
                break

    def set_token(self, serial, secret, region):
        self.serial = serial
        self.secret = secret
        self.region = region

    def get_time_offset(self):
        res = urllib2.urlopen(M_URL % self.region + M_SYNC).read()
        self.offset = int(time.time() * 1000) - sum(ord(res[7 - i]) << (i * 8) for i in range(8))

    def get_password(self):
        t = (int(time.time() * 1000) + self.offset) / 30000
        src = bytearray([0, 0, 0, 0] + [c for c in struct.pack('>L', t)])
        key = bytearray(self.secret.decode('hex'))
        raw_hmac = bytearray(hmac.new(key, src, hashlib.sha1).digest())
        pos = raw_hmac[19] & 0x0f
        auth = str(raw_hmac[pos:pos+4])
        tmp = struct.unpack('>l', auth)[0]
        code = (tmp & 0x7FFFFFFF) % (10**8)
        return code

if __name__ == '__main__':
    usage = 'usage: %prog <option> <token_name>'
    parser = OptionParser(usage)
    parser.add_option('-n', '--new', action='store_true', help='request new token from server', default=False)
    parser.add_option('-g', '--generate', action='store_true', help='generate password for existing token', default=False)
    parser.add_option('-l', '--list', action='store_true', help='get a list of existing tokens', default=False)
    parser.add_option('-r', '--region', dest='region', help='set the region (default: %default)', default='eu')
    (options, args) = parser.parse_args()
    tokens = {}
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                tokens[row[0]] = (row[1], row[2], row[3])
    f = open(TOKEN_FILE, 'ab')
    if options.new:
        t = Token()
        t.generate()
        writer = csv.writer(f)
        writer.writerow([args[0], t.serial, t.secret, t.region])
    elif options.list:
        print '%-24s%-24s' % ('Token name (region)', 'Token serial')
        for (k, v) in tokens.items():
            print '%-24s%-24s' % ('%s (%s)' % (k, v[2]), v[0])
    elif options.generate:
        if args[0] not in tokens.keys():
            print '[!] Unknown token name'
        else:
            t = Token()
            tmp = tokens[args[0]]
            t.set_token(tmp[0], tmp[1], tmp[2])
            t.get_time_offset()
            print 'Password for %s: %s' % (args[0], t.get_password())
    else:
        parser.print_help()
    f.close()
