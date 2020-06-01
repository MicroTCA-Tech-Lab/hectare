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


def gen_vhdl_axi(filename):
    rdlc = RDLCompiler()
    rdlc.compile_file(filename)
    root = rdlc.elaborate()

    walker = RDLWalker(unroll=True)
    listener = HectareListener()
    walker.walk(root, listener)

    vhdl = HectareVhdlGen(listener.addrmaps[0], input_filename=filename)
    s = vhdl.generate_string()
    pre, _ = os.path.splitext(filename)
    out_file = open(pre + ".vhd", "w")
    out_file.write(s)
    out_file.close()


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
        gen_vhdl_axi(args.filename)
    except RDLCompileError as err:
        print(err)
        sys.exit(1)


if __name__ == "__main__":
    main()
