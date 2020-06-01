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


def gen_vhdl_axi(in_filename, out_filename):
    rdlc = RDLCompiler()
    rdlc.compile_file(in_filename)
    root = rdlc.elaborate()

    walker = RDLWalker(unroll=True)
    listener = HectareListener()
    walker.walk(root, listener)
    print("Parsing finished.")

    vhdl = HectareVhdlGen(listener.addrmaps[0], input_filename=in_filename)
    s = vhdl.generate_string()
    print("Generating {0} ...".format(out_filename))
    out_file = open(out_filename, "w")
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
    parser.add_argument(
        "--axi-vhdl",
        nargs=1,
        dest="vhdl_name",
        type=str,
        help="generate AXI4-Lite slave",
    )
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    try:
        if args.vhdl_name is not None:
            gen_vhdl_axi(args.filename, args.vhdl_name[0])
    except RDLCompileError as err:
        print(err)
        sys.exit(1)

    print("Done.")


if __name__ == "__main__":
    main()
