#!/usr/bin/python3

import os, sys
import socket
import argparse
from smtplib import SMTP_SSL as SMTP
from email.utils import formatdate
from email.message import EmailMessage
from email.headerregistry import Address


def get_host_name():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    name, cnames, ips = socket.gethostbyaddr(ip)
    return name


class Mailer(object):
    def __init__(self,
        server, user, passwd, to, sender,
        content, subject, html=None
    ):
        self.server = server
        self.user = user
        self.passwd = passwd
        self.content = content
        self.html = html
        self.to = to
        self.sender = sender or self.user
        self.subject = subject


    def send(self):
        try:
            msg = EmailMessage()
            msg['Date'] = formatdate()
            msg['Subject'] = self.subject
            msg['From'] = Address('Alpha Geeks', *self.sender.split('@'))
            msg['To'] = tuple(
                Address('System Admin', *t.split('@')) for t in self.to
            )
            msg.set_content(self.content)
            if self.html is not None:
                msg.add_alternative("""<html>
                <head><title>{title}</title>
                </head><body><pre>{body}</pre>
                </body></html>
                """.format(
                    title=self.subject,
                    body=self.html
                ), subtype='html')
            with SMTP(self.server) as con:
                con.login(self.user, self.passwd)
                con.send_message(msg)
        except Exception as e:
            sys.exit("mail failed: %s" % str(e))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Send a simple email',
    )
    parser.add_argument('-v', '--verbose',
        help='be verbose',
        action='store_true',
    )
    parser.add_argument('-n', '--dry-run',
        help='don\'t actually do anything',
        action='store_true',
    )
    parser.add_argument('-H', '--html',
        help='attach html alternative',
        metavar='HTML'
    )
    parser.add_argument('-s', '--subj',
        help='subject of the email',
        metavar='SUBJ',
        default='System message from %s' % get_host_name()
    )
    parser.add_argument('-S', '--host',
        help='SMTP server to use',
        required=True,
        metavar='HOST',
    )
    parser.add_argument('-t', '--to',
        help="recipient's email address",
        action='append',
        required=True,
        metavar='ADDR',
    )
    parser.add_argument('-u', '--user',
        help='username for the SMTP server',
        required=True,
        metavar='NAME',
    )
    parser.add_argument('-p', '--pwd',
        help='password for the SMTP server user',
        required=True,
        metavar='WORD',
    )
    parser.add_argument('message',
        help='the message(s) to send',
        metavar='message',
        nargs='+',
    )

    args = parser.parse_args()

    content=' '.join(args.message)

    if len(args.message) == 1 and args.message[0] == '-':
        content = sys.stdin.read()

    try:
        mail = Mailer(
            server=args.host,
            user=args.user,
            passwd=args.pwd,
            to=args.to,
            content=content,
            html=args.html,
            sender=args.user,
            subject=args.subj or None
        )
        if args.dry_run:
            print('DRY RUN: (Sending skipped)')
        else:
            mail.send()
    except Exception as e:
        print("Error: {}".format(e))
    else:
        args.verbose and print('Success!')

    if args.verbose:
        print('\n'.join('%-8s : %s' % (k,v)
            for k,v in mail.__dict__.items()
        ))
