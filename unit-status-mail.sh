#!/bin/bash

get_secret() {
    python3 <<PYTHON
import json
with open('/mnt/AGCSWWW/data/conf/secrets.json') as f:
    print(json.load(f)["$1"])
PYTHON
}

err () {
    echo "FAIL: Status mail NOT sent to: $MAILTO for unit: $UNIT"
    echo ${@:--n}
    exit 1
}

trap err ERR
exec {STDOUT}>&1 >&2
set -e

MAILTO="root@alphageek.xyz"
UNIT="${1:-$(err)}"
UNITSTATUS="$(systemctl status $UNIT || true)"
for e in "${@:2}"; do
  EXTRA+="$e"$'\n'
done

~django/site/bin/mailer.py \
    -s "Status mail for unit: $UNIT" \
    -S "$(get_secret email_host)" \
    -u "$(get_secret email_host_user)" \
    -p "$(get_secret email_host_pass)" \
    -t "$MAILTO" - <<EOF
Status report for unit: $UNIT
$EXTRA

$UNITSTATUS
EOF

exec >&${STDOUT} {STDOUT}>&-
echo "Status mail sent to: $MAILTO for unit: $UNIT"
