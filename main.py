#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse
import time
import logging
import sys

import config
from lib.tcpserver import UrandomServer
from lib.database import setup_db

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='botshitter')
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='hostname'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=1337,
        help='port number'
    )
    parser.add_argument(
        '--logfile',
        default='./logs/debug.log',
        help='debug file'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        default=False,
        help='enable verbose output'
    )
    args = parser.parse_args()

    # setup logging
    # debug into file
    logging.basicConfig(
        filename=args.logfile,
        filemode='w',
        level=logging.DEBUG,
        format=config.LOG_FORMAT,
        datefmt=config.LOG_DATETIME_FORMAT
    )

    # console logging
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.DEBUG if args.verbose else logging.INFO)
    console.setFormatter(logging.Formatter(config.LOG_FORMAT, datefmt=config.LOG_DATETIME_FORMAT))
    logging.getLogger().addHandler(console)

    logger = logging.getLogger("Urandomizer")
    logger.info('setup db...')
    setup_db(config.DATABASE)

    logger.info('creating server...')
    server = UrandomServer(args.host, args.port)
    logger.info('starting server...')
    server.start()
    logger.info('serve forever... ctrl+c to stop')
    while True:
        try:
            time.sleep(0.5)
        except KeyboardInterrupt:
            logger.info('hit ctrl+c')
            break
    server.stop()

