#!/usr/bin/python3

import os, sys
import socket
import argparse
from smtplib import SMTP_SSL as SMTP
from email.mime.text import MIMEText
from email.utils import formatdate


def get_host_name():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    name, cnames, ips = socket.gethostbyaddr(ip)
    return name


class Mailer(object):
    def __init__(self,
        server, user, passwd, to,
        content, sender=None, subject=None
    ):
        self.server = server
        self.user = user
        self.passwd = passwd
        self.content = content
        self.to = to
        self.sender = sender or self.user
        self.subject = subject or (
            'System message from %s' % get_host_name()
        )

    def send(self):
        try:
            msg = MIMEText(self.content, 'plain', 'utf-8')
            msg['Subject'] = self.subject
            msg['From'] = self.sender
            msg['To'] = ', '.join(self.to)
            msg['Date'] = formatdate()
            con = SMTP(self.server)
            con.set_debuglevel(False)
            con.login(self.user, self.passwd)
            try:
                con.sendmail(self.sender, self.to, msg.as_string())
            finally:
                con.quit()
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
    parser.add_argument('-T', '--test',
        help='Run in test mode',
        action='store_true',
    )
    parser.add_argument('-s', '--subject',
        help='Subject of the email',
        metavar='SUBJECT',
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

    if ('-T' or '--test') in sys.argv:
        test_args = []
        for k,v in defaults.items():
            test_args.append('--%s' % k)
            test_args.append('%s' % v)
        import_args.extend(test_args + sys.argv[1:])
        import_args.append('This is a test message')
    else:
        import_args.extend(sys.argv[1:])

    args = parser.parse_args(import_args)
    text = ' '.join(args.message)
    mail = Mailer(
        server=args.server,
        user=args.user,
        passwd=args.password,
        to=args.to,
        content=text,
        sender=args.user,
        subject=args.subject or None
    )

    try:
        mail.send()
    except Exception as e:
        print("Error: {}".format(e))
    else:
        args.verbose and print('Success!')

    if args.verbose:
        print('\n'.join('%-8s : %s' % (k,v)
            for k,v in mail.__dict__.items()
        ))

