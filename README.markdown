PYBNA
=====

### Description

pybna is a battle.net authenticator token generator, based on cheald's FlexAuth (<https://github.com/cheald/FlexAuth>)

### Installation

1. clone source: `git clone git@github.com:potato/pybna.git && cd pybna`
2. open pybna.py, and edit `TOKEN_FILE` (the default token file path is ./token.csv)

### Usage

    pybna.py <option> <token_name>
        -h, --help            show this help message and exit
        -n, --new             request new token from server
        -g, --generate        generate password for existing token
        -l, --list            get a list of existing tokens
        -r REGION, --region=REGION
                        set the region (default: eu)

### License

This file is part of pybna.

pybna is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pybna is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with pybna. If not, see <http://www.gnu.org/licenses/>.

(C) 2012- by Laszlo Hammerl, <mail@crazypotato.tk>