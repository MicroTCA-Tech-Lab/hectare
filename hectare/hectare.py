#!/usr/bin/env python3

"""
Copyright (c) 2020 Deutsches Elektronen-Synchrotron DESY.
"""

import argparse
import logging
import os
import sys

from systemrdl import RDLCompileError, RDLCompiler, RDLWalker

from hectare._HectareListener import HectareListener
from hectare._HectareVhdlGen import HectareVhdlGen


def gen_vhdl_axi(in_filename, out_filename):

    if out_filename[-4:] != ".vhd":
        raise ValueError("output filename is expected to have .vhd extension")

    rdlc = RDLCompiler()
    rdlc.compile_file(in_filename)
    root = rdlc.elaborate()

    walker = RDLWalker(unroll=True)
    listener = HectareListener()
    walker.walk(root, listener)
    print("Parsing finished.")

    vhdl_gen = HectareVhdlGen(listener.addrmaps[0], input_filename=in_filename)
    s_pkg = vhdl_gen.generate_package()
    s_vhdl = vhdl_gen.generate_string()

    print("Generating {0} ...".format(out_filename))
    out_file = open(out_filename, "w")
    out_file.write(s_vhdl)
    out_file.close()

    if s_pkg is not None:
        pkg_filename = out_filename.replace(".vhd", "_pkg.vhd")
        print("Generating {0} ...".format(pkg_filename))
        out_file = open(pkg_filename, "w")
        out_file.write(s_pkg)
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
