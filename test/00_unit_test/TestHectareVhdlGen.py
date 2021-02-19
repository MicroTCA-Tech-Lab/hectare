#! /usr/bin/env python3

"""
Copyright (c) 2020 Deutsches Elektronen-Synchrotron DESY

See LICENSE.txt for license details.
"""

import enum
import sys
import unittest

from systemrdl.rdltypes import AccessType

from hectare._hectare_types import Field, Register
from hectare._HectareVhdlGen import HectareVhdlGen


class TestHectareVhdlGen(unittest.TestCase):
    DATA_W_BYTES = 4

    def test_single_addr(self):
        reg = Register("myreg", 8)
        s = HectareVhdlGen._gen_single_addr(reg, self.DATA_W_BYTES)
        self.assertEqual(s, "constant C_ADDR_MYREG : integer := 2;")

    def test_single_field_range(self):
        field = Field("myfield", 8, 15, AccessType.rw, AccessType.rw, swmod=False)
        l = HectareVhdlGen._gen_single_field_range("myreg", field)
        self.assertEqual(l[0], "constant C_FIELD_MYREG_MYFIELD_MSB : integer := 15;")
        self.assertEqual(l[1], "constant C_FIELD_MYREG_MYFIELD_LSB : integer := 8;")

    def test_gen_single_reg(self):
        reg = Register("myreg", 8)
        s = HectareVhdlGen._gen_single_reg(reg, self.DATA_W_BYTES)
        self.assertEqual(s, "signal reg_myreg : std_logic_vector(32-1 downto 0);")

    def test_gen_single_port(self):
        field = Field("myfield", 8, 15, AccessType.rw, AccessType.rw, swmod=False)
        l = HectareVhdlGen._gen_single_port("myreg", field)
        self.assertEqual(l[0], "myreg_myfield_o : out std_logic_vector(7 downto 0);")
        self.assertEqual(l[1], "myreg_myfield_i : in std_logic_vector(7 downto 0);")

    def test_gen_single_port_onebit(self):
        field = Field("myfield", 8, 8, AccessType.rw, AccessType.rw, swmod=False)
        l = HectareVhdlGen._gen_single_port("myreg", field)
        self.assertEqual(l[0], "myreg_myfield_o : out std_logic;")
        self.assertEqual(l[1], "myreg_myfield_i : in std_logic;")

    def test_gen_single_port_swmod(self):
        field = Field("myfield", 8, 15, AccessType.r, AccessType.rw, swmod=True)
        l = HectareVhdlGen._gen_single_port("myreg", field)
        self.assertEqual(len(l), 2, "expect to generate _o and _swmod ports")
        self.assertEqual(l[0], "myreg_myfield_o : out std_logic_vector(7 downto 0);")
        self.assertEqual(l[1], "myreg_myfield_swmod : out std_logic;")

    def test_gen_single_hw_access_reg(self):
        field = Field("myfield", 8, 15, AccessType.rw, AccessType.rw, swmod=False)
        l = HectareVhdlGen._gen_single_hw_access("myreg", field, in_reg=True)
        self.assertEqual(l[0], "myreg_myfield_o <= reg_myreg(15 downto 8);")
        self.assertEqual(
            l[1], "reg_myreg(15 downto 8) <= myreg_myfield_i when rising_edge(clk);"
        )

    def test_gen_single_hw_access_no_reg(self):
        field = Field("myfield", 8, 15, AccessType.rw, AccessType.rw, swmod=False)
        l = HectareVhdlGen._gen_single_hw_access("myreg", field, in_reg=False)
        self.assertEqual(l[0], "myreg_myfield_o <= reg_myreg(15 downto 8);")
        self.assertEqual(l[1], "reg_myreg(15 downto 8) <= myreg_myfield_i;")

    def test_gen_single_hw_access_no_reg_onebit(self):
        field = Field("myfield", 8, 8, AccessType.rw, AccessType.rw, swmod=False)
        l = HectareVhdlGen._gen_single_hw_access("myreg", field, in_reg=True)
        self.assertEqual(l[0], "myreg_myfield_o <= reg_myreg(8);")
        self.assertEqual(l[1], "reg_myreg(8) <= myreg_myfield_i when rising_edge(clk);")

    def test_gen_single_hw_access_enum_out(self):
        class ColorSel(enum.Enum):
            RED = 0
            GREEN = 1
            BLUE = 2

        field = Field(
            "myfield", 0, 2, AccessType.r, AccessType.rw, swmod=False, encode=ColorSel
        )
        l = HectareVhdlGen._gen_single_hw_access("myreg", field, in_reg=True)
        self.assertEqual(
            l[0],
            "myreg_myfield_o <= ColorSel_t'val(to_integer(unsigned(reg_myreg(2 downto 0))));",
        )

    def test_gen_single_hw_access_enum_in(self):
        class ColorSel(enum.Enum):
            RED = 0
            GREEN = 1
            BLUE = 2

        field = Field(
            "myfield", 0, 2, AccessType.w, AccessType.rw, swmod=False, encode=ColorSel
        )
        l = HectareVhdlGen._gen_single_hw_access("myreg", field, in_reg=True)
        self.assertEqual(
            l[0],
            "reg_myreg(2 downto 0) <= std_logic_vector(to_unsigned(ColorSel_t'pos(myreg_myfield_i), 3)) when rising_edge(clk);",
        )

    def test_gen_single_reg_swmod_no_swmod(self):
        reg = Register("myreg", 0)
        reg.fields.append(
            Field("myfield1", 0, 7, AccessType.rw, AccessType.rw, swmod=False)
        )
        reg.fields.append(
            Field("myfield2", 8, 15, AccessType.rw, AccessType.rw, swmod=False)
        )
        swmod_reg = HectareVhdlGen._gen_single_reg_swmod(reg, self.DATA_W_BYTES)
        self.assertIsNone(
            swmod_reg, "if none of the fields has swmod, no swmod reg is generated"
        )

    def test_gen_single_reg_swmod_with_swmod(self):
        reg = Register("myreg", 0)
        reg.fields.append(
            Field("myfield1", 0, 7, AccessType.rw, AccessType.rw, swmod=False)
        )
        reg.fields.append(
            Field("myfield2", 8, 15, AccessType.rw, AccessType.rw, swmod=True)
        )
        swmod_reg = HectareVhdlGen._gen_single_reg_swmod(reg, self.DATA_W_BYTES)
        self.assertEqual(
            swmod_reg,
            "signal reg_myreg_swmod : std_logic;",
            "if at least one reg has swmod attribute set, reg is generated",
        )

    def test_gen_single_enum_type(self):
        class ColorSel(enum.Enum):
            RED = 0
            GREEN = 1
            BLUE = 2

        field = Field(
            "myfield", 8, 15, AccessType.rw, AccessType.rw, swmod=False, encode=ColorSel
        )

        lines = HectareVhdlGen._gen_single_enum_type(field)
        self.assertEqual(
            len(lines),
            1 + 3 + 1,
            "one line per each item, declaration and closing bracket",
        )
        self.assertTrue("RED" in lines[1])
        self.assertTrue("GREEN" in lines[2])
        self.assertTrue("BLUE" in lines[3])

    def test_gen_single_enum_type_invalid(self):
        """ generates un-supported encoding (inc != 1) and checks if generator raises expection """

        class ColorSelInvalid(enum.Enum):
            RED = 0
            GREEN = 1
            BLUE = 10  # <- this is not supported

        field = Field(
            "myfield",
            8,
            15,
            AccessType.rw,
            AccessType.rw,
            swmod=False,
            encode=ColorSelInvalid,
        )

        self.assertRaises(AssertionError, HectareVhdlGen._gen_single_enum_type, field)

    def test_gen_single_reset_assignment(self):

        RESET_VAL = 0x12

        field = Field(
            "myfield", 8, 15, AccessType.rw, AccessType.rw, swmod=False, reset=RESET_VAL
        )

        line = HectareVhdlGen._gen_single_reset_assignment("myreg", field)
        assign_val = line.split("<=")[1].strip().replace(";", "")

        self.assertEqual(assign_val, '"{0:08b}"'.format(RESET_VAL), "reset value")
        self.assertEqual(len(assign_val), 8+2, "assign value must be of same size as the field")


if __name__ == "__main__":
    unittest.main()
