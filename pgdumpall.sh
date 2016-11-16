#!/bin/bash

test `whoami` = root || {
    echo 'Must be root'
    exit 1
}

set -e
FNAME="${1:-agcs_db_all.sql}"
sudo -iu postgres /usr/bin/pg_dumpall -c --if-exists > "$FNAME"
gzip --rsyncable -n "$FNAME"
chmod 0400 "${FNAME}.gz"
