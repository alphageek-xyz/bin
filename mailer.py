#!/usr/bin/python3

import os, sys
import socket
import argparse
from smtplib import SMTP_SSL as SMTP
from email.utils import formatdate
from email.message import EmailMessage
from email.headerregistry import Address
from email.utils import make_msgid


def get_host_name():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    name, cnames, ips = socket.gethostbyaddr(ip)
    return name


class Mailer(object):
    def __init__(self,
        server, user, passwd, to, content,
        html=None, sender=None, subject=None
    ):
        self.server = server
        self.user = user
        self.passwd = passwd
        self.content = content
        self.html = html
        self.to = to
        self.sender = sender or self.user
        self.subject = subject or (
            'System message from %s' % get_host_name()
        )

    def send(self):
        try:
            msg = EmailMessage()
            msg['Subject'] = self.subject
            msg['From'] = Address('Alpha Geeks', *self.sender.split('@'))
            msg['To'] = tuple(
                Address('System Admin', *t.split('@'))
                    for t in self.to
            )
            msg['Date'] = formatdate()
            msg.set_content(self.content)
            if self.html is not None:
                msg.add_alternative("""
                <html><head>
                <title>{title}</title>
                </head><body>
                <pre>{body}</pre>
                </body></html>
                """.format(title=self.subject, body=self.html), subtype='html')
            with SMTP(self.server) as con:
                con.login(self.user, self.passwd)
                con.send_message(msg)
        except Exception as e:
            sys.exit("mail failed: %s" % str(e))


if __name__ == '__main__':
    defaults = {
        'server'  : 'smtp.zoho.com',
        'user'    : 'no-reply@alphageek.xyz',
        'to'      : 'root@alphageek.xyz',
        'subject' : 'System message from %s' % get_host_name(),
    }

    import_args = []

    for i in ['server', 'user', 'password', 'to']:
        v = 'MAILER_' + i.upper()
        os.environ.get(v) and import_args.extend(
            ['--' + i, os.environ[v]]
        )

    parser = argparse.ArgumentParser(
        description='Send a simple email',
    )
    parser.add_argument('-v', '--verbose',
        help='Be verbose',
        action='store_true',
    )
    parser.add_argument('-n', '--dry-run',
        help='Run in test mode',
        action='store_true',
    )
    parser.add_argument('-H', '--html',
        help='Attach html alternative',
        metavar='HTML'
    )
    parser.add_argument('-s', '--subject',
        help='Subject of the email',
        metavar='SUBJECT',
        default='System message from %s' % get_host_name()
    )
    parser.add_argument('-S', '--server',
        help='SMTP server to use',
        required=True,
        metavar='HOST',
    )
    parser.add_argument('-t', '--to',
        help="Recipient's email address",
        action='append',
        required=True,
        metavar='EMAIL',
    )
    parser.add_argument('-u', '--user',
        help='Username for the SMTP server',
        required=True,
        metavar='NAME',
    )
    parser.add_argument('-p', '--password',
        help='Password for the SMTP server user',
        required=True,
        metavar='PASS',
    )
    parser.add_argument('message',
        help='The message(s) to send',
        metavar='message',
        nargs='+',
    )

    if ('-n' or '--dry-run') in sys.argv:
        test_args = []
        for k,v in defaults.items():
            test_args.append('--%s' % k)
            test_args.append('%s' % v)
        import_args.extend(test_args + sys.argv[1:])
        import_args.append('This is a test message')
    else:
        import_args.extend(sys.argv[1:])

    args = parser.parse_args(import_args)

    try:
        mail = Mailer(
            server=args.server,
            user=args.user,
            passwd=args.password,
            to=args.to,
            content=' '.join(args.message),
            html=args.html,
            sender=args.user,
            subject=args.subject or None
        )
        mail.send()
    except Exception as e:
        print("Error: {}".format(e))
    else:
        args.verbose and print('Success!')

    if args.verbose:
        print('\n'.join('%-8s : %s' % (k,v)
            for k,v in mail.__dict__.items()
        ))

