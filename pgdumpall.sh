#!/bin/bash

err () {
    [[ -n "$FNAME" ]] && [[ -f "$FNAME" ]] &&
        rm -vf "$FNAME"{,.gz} || true
    echo "Usage: ${BASH_SOURCE##*/} [OUTFILE]"
    echo ${@:--ne}
    exit 1
}

exec >&2
trap err ERR
set -e

test `whoami` = root || err 'Must be root'
FNAME="${1:-agcs_db_all.sql}"
sudo -iu postgres /usr/bin/pg_dumpall -c --if-exists >"$FNAME"
gzip --rsyncable -n "$FNAME"
chmod 0400 "${FNAME}.gz"
