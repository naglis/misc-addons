# -*- coding: utf-8 -*-
# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import argparse
import os
import sys

from odoo import SUPERUSER_ID, api, cli, registry


class Uml(cli.Command):
    '''Update module list in a given database.'''

    def run(self, cmd_args):
        parser = argparse.ArgumentParser(
            prog='%s uml' % os.path.basename(sys.argv[0]),
            description=self.__doc__,
        )
        parser.add_argument(
            'database',
            metavar='DB_NAME',
            help='specify the database name',
        )

        args = parser.parse_args(args=cmd_args)
        with api.Environment.manage():
            with registry(args.database).cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                updated, added = env['ir.module.module'].update_list()
                sys.stderr.write(
                    '%d modules updated, %d new added\n' % (updated, added))
