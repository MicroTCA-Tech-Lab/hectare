#! /usr/bin/env python3

import sys
import unittest

from systemrdl.rdltypes import AccessType

# isort: off
sys.path.append("../../hectare")
from _HectareVhdlGen import HectareVhdlGen
from _hectare_types import Field, Register

# isort: on


class TestHectareVhdlGen(unittest.TestCase):
    DATA_W_BYTES = 4

    def test_single_addr(self):
        reg = Register("myreg", 8)
        s = HectareVhdlGen._gen_single_addr(reg, self.DATA_W_BYTES)
        self.assertEqual(s, "constant C_ADDR_MYREG : integer := 2;")

    def test_single_field_range(self):
        field = Field("myfield", 8, 15, AccessType.rw, AccessType.rw)
        l = HectareVhdlGen._gen_single_field_range("myreg", field)
        self.assertEqual(l[0], "constant C_FIELD_MYREG_MYFIELD_MSB : integer := 15;")
        self.assertEqual(l[1], "constant C_FIELD_MYREG_MYFIELD_LSB : integer := 8;")

    def test_gen_single_reg(self):
        reg = Register("myreg", 8)
        s = HectareVhdlGen._gen_single_reg(reg, self.DATA_W_BYTES)
        self.assertEqual(s, "signal reg_myreg : std_logic_vector(32-1 downto 0);")

    def test_gen_single_port(self):
        field = Field("myfield", 8, 15, AccessType.rw, AccessType.rw)
        l = HectareVhdlGen._gen_single_port("myreg", field)
        self.assertEqual(l[0], "myreg_myfield_o : out std_logic_vector(7 downto 0);")
        self.assertEqual(l[1], "myreg_myfield_i : in std_logic_vector(7 downto 0);")

    def test_gen_single_hw_access_reg(self):
        field = Field("myfield", 8, 15, AccessType.rw, AccessType.rw)
        l = HectareVhdlGen._gen_single_hw_access("myreg", field, in_reg=True)
        self.assertEqual(l[0], "myreg_myfield_o <= reg_myreg(15 downto 8);")
        self.assertEqual(
            l[1], "reg_myreg(15 downto 8) <= myreg_myfield_i when rising_edge(clk);"
        )

    def test_gen_single_hw_access_no_reg(self):
        field = Field("myfield", 8, 15, AccessType.rw, AccessType.rw)
        l = HectareVhdlGen._gen_single_hw_access("myreg", field, in_reg=False)
        self.assertEqual(l[0], "myreg_myfield_o <= reg_myreg(15 downto 8);")
        self.assertEqual(l[1], "reg_myreg(15 downto 8) <= myreg_myfield_i;")


if __name__ == "__main__":
    unittest.main()
