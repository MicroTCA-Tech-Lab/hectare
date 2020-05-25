#!/usr/bin/env python3

"""
Copyright (c) 2020 Deutsches Elektronen-Synchrotron DESY.
"""

import argparse
import logging
import os
import sys

from systemrdl import RDLCompileError, RDLCompiler, RDLWalker

from _HectareListener import HectareListener
from _HectareVhdlGen import HectareVhdlGen


def main():
    parser = argparse.ArgumentParser(
        description="HECTARE - Hamburg Elegant CreaTor from Accelera systemrdl to REgisters"
    )
    parser.add_argument("filename", type=str, help=".rdl file")
    parser.add_argument(
        "--debug", action="store_true", help="enable debugging information"
    )
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    try:
        rdlc = RDLCompiler()
        rdlc.compile_file(args.filename)
        root = rdlc.elaborate()

        walker = RDLWalker(unroll=True)
        listener = HectareListener()
        walker.walk(root, listener)

        vhdl = HectareVhdlGen(listener.addrmaps[0])
        print(vhdl.generate_string())

    except RDLCompileError as err:
        print(err)
        sys.exit(1)


if __name__ == "__main__":
    main()
