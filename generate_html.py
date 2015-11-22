#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse
import logging
import json
import sys

import config
from lib.database import setup_db, UrandomizationStorage

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='generates .html from database')
    parser.add_argument('--database', default=config.DATABASE, help='sqlite database')
    parser.add_argument('--verbose', action='store_true', default=False, help='verbose infos')
    args = parser.parse_args()

    # setup logging
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG if args.verbose else logging.INFO,
        format=config.LOG_FORMAT,
        datefmt=config.LOG_DATETIME_FORMAT
    )

    logging.info('setup_db...')
    setup_db(args.database)

    datas = []
    for entry in UrandomizationStorage().get_urandomizations():
        datas.append({
            "startTime": str(entry.start_time),
            "stopTime": str(entry.stop_time),
            "totalTime": str(entry.stop_time - entry.start_time),
            "byteCount": entry.byte_count,
            "ipAddress": entry.ip_address
        })

    html_doc = """<!DOCTYPE html>
<html>
    <head>
        <title>Urandomizater</title>
        <link rel="stylesheet" media="all" href="https://s3.amazonaws.com/dynatable-docs-assets/css/jquery.dynatable.css" />
        <script type='text/javascript' src='https://s3.amazonaws.com/dynatable-docs-assets/js/jquery-1.9.1.min.js'></script>
        <script type='text/javascript' src='https://s3.amazonaws.com/dynatable-docs-assets/js/jquery.dynatable.js'></script>
        <script type='text/javascript'>
            $(document).ready( function() {
                $("#tableau").dynatable({
                    dataset: {
                        records: JSON.parse($('#datas').text())
                    },
                    features: {
                        paginate: false,
                        recordCount: false,
                        perPageSelect: false
                    }
                });
            });
        </script>
    </head>
    <body>
        <table class="table table-striped" id="tableau">
            <thead>
                <th>Start time</th>
                <th>Stop time</th>
                <th>Total time</th>
                <th>Byte count</th>
                <th>Ip address</th>
            </thead>
            <tbody>
            </tbody>
        </table>
        <script id="datas">"""
    html_doc += json.dumps(datas)
    html_doc += """
        </script>
    </body>
</html>
    """

    with open('results.html', 'wb') as f:
        f.write(html_doc)
