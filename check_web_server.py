#!/usr/bin/env python3

import os, sys
import json
from subprocess import Popen, PIPE, DEVNULL


if __name__ == '__main__':
    services = ['alphageek', 'uwsgi', 'memcached']
    statuses = []

    for service in services:
        p = Popen(
            '/bin/systemctl --no-pager status %s.service' % service,
            stdout=PIPE, stderr=PIPE, shell=True
        )
        statuses.append({
            'name': service,
            'code': os.waitpid(p.pid, 0)[1],
            'data': '\n'.join(i.decode() for i in p.communicate())
        })

    if not all(not i['code'] for i in statuses):
        heading = 'A required service is not running. Fix it NOW!'
        with open('/var/local/agcs/conf/secrets.json') as f:
            secrets = json.load(f)
        try:
            from mailer import Mailer
            mail = Mailer(
                server='smtp.zoho.com',
                subject='Server Problem',
                to=['root@alphageek.xyz'],
                sender=secrets['email_host_user'],
                user=secrets['email_host_user'],
                passwd=secrets['email_host_pass'],
                content=heading,
                html='%s\n\n%s' % (heading,
                    '\n'.join(s['data'] for s in statuses)
                )
            )
            mail.send()
        except Exception as e:
            print("%s: Error sending email\n%s" % (
                os.path.basename(sys.argv[0]), str(e)
            ), file=sys.stderr)
        else:
            print('Mail sent')
    else:
        print('All services running')
