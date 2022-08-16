#!/usr/bin/python
# -*- coding: utf-8 -*-

import base64
import json
import logging
import urllib.error
import urllib.parse
import urllib.parse
import urllib.request
from argparse import ArgumentParser

__all__ = ['main']


gfwlist_url = 'https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt'

def u(s, encoding="utf8"):
    if isinstance(s, bytes):
        return str(s, encoding)
    return str(s)

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('-i', '--input', dest='input',
                        help='path to gfwlist', metavar='GFWLIST')
    parser.add_argument('-f', '--file', dest='output', required=True,
                        help='path to output pac', metavar='PAC')
    parser.add_argument('-p', '--proxy', dest='proxy', required=True,
                        help='the proxy parameter in the pac file, '
                             'for example, "SOCKS5 127.0.0.1:1080;"',
                        metavar='PROXY')
    parser.add_argument('--user-rule', dest='user_rule',
                        help='user rule file, which will be appended to'
                             ' gfwlist')
    return parser.parse_args()


def decode_gfwlist(content):
    # decode base64 if have to
    try:
        if '.' in content:
            raise Exception()
        return base64.b64decode(content)
    except:
        return content


def get_hostname(something):
    try:
        # quite enough for GFW
        if not something.startswith('http:'):
            something = 'http://' + something
        r = urllib.parse.urlparse(something)
        return r.hostname
    except Exception as e:
        logging.error(e)
        return None


def add_domain_to_set(s, something):
    hostname = get_hostname(something)
    if hostname is not None:
        s.add(hostname)


def combine_lists(content, user_rule=None):
    builtin_rules = open("resources/builtin.txt", "rb").read().splitlines(False)
    gfwlist = content.splitlines(False)
    gfwlist.extend(builtin_rules)
    if user_rule:
        gfwlist.extend(user_rule.splitlines(False))
    return gfwlist


def generate_pac_precise(rules, proxy):
    def grep_rule(rule):
        if rule:
            if rule.startswith('!'):
                return None
            if rule.startswith('['):
                return None
            return rule
        return None
    # render the pac file
    proxy_content = open('resources/abp.js').read()
    rules = list(filter(grep_rule, rules))
    proxy_content = proxy_content.replace('__PROXY__', json.dumps(str(proxy)))
    proxy_content = proxy_content.replace('__RULES__',
                                          json.dumps(rules, indent=2))
    return proxy_content


def main():
    args = parse_args()
    user_rule = None
    if (args.input):
        with open(args.input, 'r') as f:
            content = f.read()
    else:
        print(('Downloading gfwlist from %s' % gfwlist_url))
        content = urllib.request.urlopen(gfwlist_url, timeout=10).read()
    if args.user_rule:
        userrule_parts = urllib.parse.urlsplit(args.user_rule)
        if not userrule_parts.scheme or not userrule_parts.netloc:
            # It's not an URL, deal it as local file
            with open(args.user_rule, 'r') as f:
                user_rule = f.read()
        else:
            # Yeah, it's an URL, try to download it
            print(('Downloading user rules file from %s' % args.user_rule))
            user_rule = urllib.request.urlopen(args.user_rule, timeout=10).read()

    content = decode_gfwlist(content)
    byte_gfwlist = combine_lists(content, user_rule)
    gfwlist = []
    for byte_gfw in byte_gfwlist:
        gfwlist.append(byte_gfw.decode('utf-8'))
    pac_content = generate_pac_precise(gfwlist, args.proxy)

    with open(args.output, 'w') as f:
        f.write(pac_content)


if __name__ == '__main__':
    main()
