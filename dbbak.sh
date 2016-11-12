#!/bin/bash

${DBBAK_DEBUG:=false} && set -x
set -e

test `whoami` = root || {
    echo must be root >&2
    exit 1
}

err() {
    test -n "$@" && echo $@
    exit 1
}

usage() {
    cat <<EOF
Usage: ${BASH_SOURCE##*/} [-h|OPTIONS]
       ${BASH_SOURCE##*/} [-nb] [-f <FNAME>] [-d <DIRNAME>]
       ${BASH_SOURCE##*/} [-F] -rf <FPATH>
EOF
    err $@
}

restore() {
    test $# -eq 1 || return 1
    declare fname="$1"
    (    [[ $(file -b "$fname" | cut -d' ' -f1) = gzip ]] &&
          gunzip -c "$fname" || cat "$fname"
    ) |    sudo -iu postgres pg_restore -cCd postgres
    echo 'GRANT ALL PRIVILEGES ON DATABASE agcs_db TO django;' | \
        sudo -iu postgres psql
}

backup() {
    test $# -eq 2 || return 1
    declare bkdir="$1" fname="$2"
    test -d "$bkdir" || mkdir -p "$bkdir"
    sudo -iu postgres /usr/bin/pg_dump -Fc agcs_db | gzip > "${bkdir}/${fname}.gz"
}

trap usage ERR

while getopts :hbrFnvd:f: opt; do
    case "$opt" in
        h) usage ;;
        b) ${restore:=false} || backup=true ;;
        r) ${backup:=false}  || restore=true ;;
        d) bkdir="$OPTARG" ;;
        f) fname="$OPTARG" ;;
        F) ${noact:-false} || noact=false ;;
        v) verbose=true ;;
        n) noact=true ;;
    esac
done

shift $((OPTIND-1))

[[ ${mode:=${restore:+restore}} ]] || mode=backup

if ${restore:-false}; then
    test -v fname || err "fname is required"
    test -v noact || noact=true
    test -f "$fname" || err "No such file: '$fname'"
    cmd='restore $fname'
else
    test -d "${bkdir:=/mnt/AGCSWWW/backups/db}" || err "No such directory: '$bkdir'"
    test -n "${fname:=agcs_db-$(date +%s).dump}" || err "Invalid fname: '$fname'"
    cmd='backup "$bkdir" "$fname"'
    noact=${noact:-false}
fi

if ${noact:-true}; then
    echo "DRY RUN (Use -F to force)"
    ! ${verbose:-false} || {
        builtin type $mode | sed 1d
        eval echo "$cmd"
    }
else
    ! ${verbose:-false} || {
        echo "Doing $mode operation"
        eval echo "$cmd"
    }
    eval "$cmd"
fi

