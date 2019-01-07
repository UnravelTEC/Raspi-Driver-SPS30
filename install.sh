#!/bin/bash
# reads out scd30 co2 sensor periodically

# Copyright © 2018 UnravelTEC
# Michael Maier <michael.maier+github@unraveltec.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# If you want to relicense this code under another license, please contact info+github@unraveltec.com.

targetdir=/usr/local/bin/

mkdir -p $targetdir

cp sps30.py $targetdir && echo "cp sps30.py $targetdir OK"
cp sps30.service /etc/systemd/system/ && echo "cp sps30.service /etc/systemd/system/ OK"
systemctl enable sps30.service && echo "systemctl enable sps30.service OK"
systemctl start sps30.service && echo "systemctl start sps30.service OK"

