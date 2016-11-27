#!/bin/bash

getalias() {
    for a in $@; do
        alias=$(sed 's/^"//g;s/"$//g'<<<"$a")
        mail -Semptystart <<<"alias $alias" |
            sed -e '1d;s/"\?\\"/"/g;' \
                -e 's/"$//g' \
                -e "s/alias $alias //g"
    done
}

err () {
    echo "FAIL: Status mail NOT sent to: $MAILTO for unit: $UNIT"
    echo ${@:--n}
    exit 1
}

trap err ERR
exec {STDOUT}>&1 >&2
set -e

MAILTO="`(getalias $(getalias admins)) || true`"
UNIT="${1:-$(err)}"
UNITSTATUS="$(systemctl status $UNIT || true)"
for e in "${@:2}"; do
  EXTRA+="$e"$'\n'
done

/usr/bin/mail \
    -s "Status mail for unit: $UNIT" \
    -A "system" admins <<EOF
Status report for unit: $UNIT
$EXTRA

$UNITSTATUS
EOF

exec >&${STDOUT} {STDOUT}>&-
echo "Status mail sent for $UNIT to: $MAILTO"
