#! /usr/bin/env python3

"""
Copyright (c) 2020 Deutsches Elektronen-Synchrotron DESY

See LICENSE.txt for license details.
"""

import logging
import os
import sys
import unittest

import hdlparse.vhdl_parser as vhdl

from hectare import hectare

CONFIG_CLEANUP_VHD_FILES = True
CONFIG_LOGGING_LEVEL = logging.DEBUG


class TestVhdlGenWithHdlparse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.logger = logging.getLogger("TestVhdlGenWithHdlparse")
        cls.logger.setLevel(CONFIG_LOGGING_LEVEL)
        for filename in os.listdir("rdl_files"):
            if filename.endswith(".rdl"):
                full_filename = os.path.join("rdl_files", filename)
                cls.logger.debug("creating VHDL AXI for  %s", full_filename)
                hectare.gen_vhdl_axi(
                    full_filename, full_filename.replace(".rdl", ".vhd")
                )

    @classmethod
    def tearDownClass(cls):
        if CONFIG_CLEANUP_VHD_FILES:
            for filename in os.listdir("rdl_files"):
                if filename.endswith(".vhd"):
                    full_filename = os.path.join("rdl_files", filename)
                    cls.logger.debug("removing %s", full_filename)
                    os.remove(full_filename)

    def test_sw_r_hw_rw(self):
        vhdl_ex = vhdl.VhdlExtractor()
        with open("rdl_files/sw-r_hw-rw.vhd", "r") as fh:
            code = fh.read()
        vhdl_objs = vhdl_ex.extract_objects_from_source(code)
        self.assertEqual(len(vhdl_objs), 1, "hdlparse should find one entity")
        self.assertEqual(vhdl_objs[0].name, "mymodule", "entity name")

        ports_o = [port for port in vhdl_objs[0].ports if port.name == "reg1_ready_o"]
        ports_i = [port for port in vhdl_objs[0].ports if port.name == "reg1_ready_i"]
        self.assertEqual(
            len(ports_o), 1, "hdlparse should find one port for the output from the reg"
        )
        self.assertEqual(
            len(ports_i), 1, "hdlparse should find one port for the input to the reg"
        )

        port_o = ports_o[0]
        self.assertEqual(port_o.name, "reg1_ready_o")
        self.assertEqual(port_o.data_type, "std_logic")
        self.assertEqual(port_o.mode, "out")

        port_i = ports_i[0]
        self.assertEqual(port_i.name, "reg1_ready_i")
        self.assertEqual(port_i.data_type, "std_logic")
        self.assertEqual(port_i.mode, "in")

    def test1(self):
        vhdl_ex = vhdl.VhdlExtractor()
        with open("rdl_files/test1.vhd", "r") as fh:
            code = fh.read()
        vhdl_objs = vhdl_ex.extract_objects_from_source(code)
        self.assertEqual(len(vhdl_objs), 1, "hdlparse should find one entity")
        self.assertEqual(vhdl_objs[0].name, "mymodule", "entity name")

        ports_swmod = [
            port for port in vhdl_objs[0].ports if port.name == "inc_dec_inc_dec_swmod"
        ]
        self.assertEqual(
            len(ports_swmod), 1, "hdlparse should find one port for the swmod signal"
        )

    def test_enum(self):
        vhdl_ex = vhdl.VhdlExtractor()
        with open("rdl_files/test_enum.vhd", "r") as fh:
            code = fh.read()
        vhdl_objs = vhdl_ex.extract_objects_from_source(code)
        self.assertEqual(len(vhdl_objs), 1, "hdlparse should find one entity")
        self.assertEqual(vhdl_objs[0].name, "mymodule", "entity name")

        ports_enum = [
            port for port in vhdl_objs[0].ports if port.name == "mode_select_mode_o"
        ]
        self.assertEqual(
            len(ports_enum),
            1,
            'hdlparse should find one port named "mode_select_mode_o"',
        )
        port_enum = ports_enum[0]
        self.assertEqual(port_enum.data_type, "ModeSelect_t")

        # check also the package
        vhdl_ex = vhdl.VhdlExtractor()
        with open("rdl_files/test_enum_pkg.vhd", "r") as fh:
            code = fh.read()
        vhdl_objs = vhdl_ex.extract_objects_from_source(code)
        self.assertEqual(
            len(vhdl_objs),
            2,
            "hdlparse should find two entitties (package and type def)",
        )
        self.assertEqual(vhdl_objs[0].name, "mymodule_pkg", "package name")
        self.assertEqual(vhdl_objs[1].name, "ModeSelect_t", "type name")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
