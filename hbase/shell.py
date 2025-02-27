#!/usr/bin/env python3

"""
@author: xi
@since: 2018-05-07
"""

import argparse
import shlex
import time

import hbase


class Shell(object):

    def __init__(self, args):
        self._args = args

        self._zk = args.zk

        self._parsers = dict()
        self._conn = None
        self._conn = None  # type: hbase.Connection
        self._ns = None

    def __enter__(self):
        self._conn = hbase.ConnectionPool(self._zk).connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def main(self):
        while True:
            prompt = '%s:> ' % (self._ns.name if self._ns is not None else '?')
            try:
                cmd = input(prompt).strip()
            except EOFError:
                break
            if len(cmd) == 0:
                continue
            if cmd == 'exit':
                break
            try:
                args = shlex.split(cmd)
                self._run_cmd(args[0], args[1:])
            except Exception as e:
                print(type(e), e)
        print('Bye bye.')

    def _run_cmd(self, cmd, args):
        attr = '_' + cmd
        if not hasattr(self, attr):
            raise RuntimeError('%s: command not found' % cmd)
        fun = getattr(self, attr)
        if not callable(fun):
            raise RuntimeError('%s: command not found' % cmd)
        fun(args)

    def _ls(self, args):
        parser_name = 'ls'
        if parser_name not in self._parsers:
            parser = argparse.ArgumentParser(prog=parser_name)
            self._parsers[parser_name] = parser
            parser.add_argument('--namespaces', '-n', action='store_true')
            parser.add_argument('--tables', '-t', action='store_true')
        args = self._parsers[parser_name].parse_args(args)

        if args.namespaces or (not args.namespaces and not args.tables):
            for ns in self._conn.namespaces():
                print(ns)
            return

        if args.tables:
            if self._ns is None:
                raise RuntimeError('No namespace selected. Please use "use [namespace]".')
            for tbl in self._ns.tables():
                print(tbl)

    def _use(self, args):
        parser_name = 'use'
        if parser_name not in self._parsers:
            parser = argparse.ArgumentParser(prog=parser_name)
            self._parsers[parser_name] = parser
            parser.add_argument('name', default=None, nargs='?')
        args = self._parsers[parser_name].parse_args(args)

        if args.name is None:
            self._ns = None
            self._tbl = None
            return

        self._ns = self._conn.namespace(args.name, create_if_not_exists=False)

    def _get(self, args):
        parser_name = 'get'
        if parser_name not in self._parsers:
            parser = argparse.ArgumentParser(prog=parser_name)
            self._parsers[parser_name] = parser
            parser.add_argument('table')
            parser.add_argument('key', nargs='?')
            parser.add_argument('--full', '-f', action='store_true', default=False)
        args = self._parsers[parser_name].parse_args(args)

        if self._ns is None:
            raise RuntimeError('No namespace selected. Please use "use [namespace]".')
        tbl = self._ns.table(args.table, create_if_not_exists=False)
        row = tbl.get(args.key) if args.key else tbl.get_one(not args.full)
        print(row)

    def _count(self, args):
        parser_name = 'count'
        if parser_name not in self._parsers:
            parser = argparse.ArgumentParser(prog=parser_name)
            self._parsers[parser_name] = parser
            parser.add_argument('table')
        args = self._parsers[parser_name].parse_args(args)

        if self._ns is None:
            raise RuntimeError('No namespace selected. Please use "use [namespace]".')
        tbl = self._ns.table(args.table, create_if_not_exists=False)
        t = time.time()
        count = tbl.count(
            verbose=lambda c, r: print('%d: %s' % (c, r.key))
        )
        t = time.time() - t
        print('\nTotal count: %d. %d seconds used.' % (count, t))


def main(args):
    with Shell(args) as shell:
        shell.main()
    return 0


if __name__ == '__main__':
    _parser = argparse.ArgumentParser()
    _parser.add_argument('--zk', required=True)
    _args = _parser.parse_args()
    exit(main(_args))
