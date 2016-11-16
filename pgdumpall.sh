#!/bin/bash

test `whoami` = root || {
    echo 'Must be root'
    exit 1
}

FNAME="agcs_db_all.sql"
set -e
sudo -iu postgres /usr/bin/pg_dumpall -c --if-exists > "${FNAME:=${1:-agcs_db_all.sql}"
gzip --rsyncable -n "$FNAME"
chmod 0400 "${FNAME}.gz"
