#! /usr/bin/env python3

"""
Copyright (c) 2020 Deutsches Elektronen-Synchrotron DESY
"""

import sys
import unittest
import os
import logging

import hdlparse.vhdl_parser as vhdl

sys.path.insert(0, "../../hectare")
import hectare

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
                hectare.gen_vhdl_axi(full_filename)

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
        self.assertEqual(port_o.data_type, "std_logic_vector(0 downto 0)")
        self.assertEqual(port_o.mode, "out")

        port_i = ports_i[0]
        self.assertEqual(port_i.name, "reg1_ready_i")
        self.assertEqual(port_i.data_type, "std_logic_vector(0 downto 0)")
        self.assertEqual(port_i.mode, "in")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
