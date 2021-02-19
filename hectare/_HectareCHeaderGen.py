"""
Copyright (c) 2020-2021 Deutsches Elektronen-Synchrotron DESY.

See LICENSE.txt for license details.
"""

import datetime
import getpass
import os
import socket
from typing import Iterator, List, Optional

from systemrdl.rdltypes import AccessType

from hectare._hectare_types import AddressMap, Field, Register


def indent_lines(ls: List[str], ident_level: int) -> Iterator[str]:
    for l in ls:
        yield " " * ident_level + l


class HectareCHeaderGen:
    def __init__(self, addrmap, input_filename=""):
        self.addrmap = addrmap
        self.cur_indent = 0
        self.data_w_bytes = 4  # 32 / 8  # TODO check regwidth
        self.input_filename = input_filename

    def generate_string(self) -> str:
        s = ""

        s += self._gen_header(self.input_filename)
        s += "\n"

        s += "#pragma once\n"

        s += "\n\n// address constants\n"
        s += "\n".join(self._gen_reg_addr())
        s += "\n"

        s += "\n\n// reset values\n"
        s += "\n".join(self._gen_reg_reset_vals())

        s += "\n\n// individual field shift\n"
        s += "\n".join(self._gen_field_shift())

        s += "\n\n// individual field mask\n"
        s += "\n".join(self._gen_field_mask())

        return s

    @staticmethod
    def _gen_header(input_filename: str, verbose: bool = False) -> str:
        s = "/* This file was automatically generated with HECTARE\n"
        s += " *\n"
        s += " * DO NOT EDIT\n"
        s += " *\n"
        s += " *   input_filename = {0}\n".format(input_filename)
        if verbose:
            s += " *   date     = {0}\n".format(datetime.datetime.now().ctime())
            s += " *   hostname = {0}\n".format(socket.gethostname())
            s += " *   user     = {0}\n".format(getpass.getuser())
        s += " */\n"
        return s

    def _gen_reg_addr(self) -> List[str]:
        comp_name = self.addrmap.name.upper()
        return [self._gen_single_addr(comp_name, reg) for reg in self.addrmap.regs]

    def _gen_reg_reset_vals(self) -> List[str]:
        # we only generate those for the values with hw=na, sw=r
        comp_name = self.addrmap.name.upper()
        reset_vals = []
        for reg in self.addrmap.regs:
            line_added = False
            for field in reg.fields:
                if field.sw_acc_type == AccessType.r and field.hw_acc_type == AccessType.na:
                    reset_vals.append(self._gen_single_reg_reset_vals(comp_name, reg.name, field))
                    line_added = True

            # to make this prettier, we only add an empty line after a group of "#define"-s
            if line_added:
                line_added = False
                reset_vals.append("")

        return reset_vals

    def _gen_field_shift(self) -> List[str]:
        comp_name = self.addrmap.name.upper()
        field_shifts = []
        for reg in self.addrmap.regs:
            for field in reg.fields:
                field_shifts.append(
                    self._gen_single_field_shift(comp_name, reg.name, field)
                )
            field_shifts.append("")

        return field_shifts

    def _gen_field_mask(self) -> List[str]:
        comp_name = self.addrmap.name.upper()
        field_mask = []
        for reg in self.addrmap.regs:
            for field in reg.fields:
                field_mask.append(
                    self._gen_single_field_mask(comp_name, reg.name, field)
                )
            field_mask.append("")

        return field_mask

    @staticmethod
    def _gen_single_enum_type(field: Field) -> str:
        # TODO
        pass

    @staticmethod
    def _gen_single_addr(comp_name: str, reg: Register) -> str:
        """ Generate an address constant for a single register

        E.g. #define MOD_ADDR_SCRATCH (0x1C)
        """

        return "#define {comp_name}_ADDR_{name} ({byte_addr})".format(
            comp_name=comp_name, name=reg.name.upper(), byte_addr=reg.addr
        )

    @staticmethod
    def _gen_single_reg_reset_vals(comp_name: str, reg_name: str, field: Field) -> str:
        """ Generate a reset values (can be used to check if matches in SW)

        this functions expects that a field has a reset value
        """

        assert field.reset is not None

        return "#define {comp_name}_{reg_name}_{field_name}_RST_VAL (0x{rst_val:x})".format(
            comp_name=comp_name,
            reg_name=reg_name,
            field_name=field.name.upper(),
            rst_val=field.reset,
        )

    @staticmethod
    def _gen_single_field_shift(comp_name: str, reg_name: str, field: Field) -> str:
        return "#define {comp_name}_{reg_name}_{field_name}_SHIFT ({shift})".format(
            comp_name=comp_name,
            reg_name=reg_name,
            field_name=field.name.upper(),
            shift=field.lsb,
        )

    @staticmethod
    def _gen_single_field_mask(comp_name: str, reg_name: str, field: Field) -> str:
        mask = (1 << (field.msb - field.lsb + 1)) - 1
        return "#define {comp_name}_{reg_name}_{field_name}_MASK (0x{mask:x})".format(
            comp_name=comp_name,
            reg_name=reg_name,
            field_name=field.name.upper(),
            mask=mask,
        )
