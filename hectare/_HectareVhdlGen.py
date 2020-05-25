"""
Copyright (c) 2020 Deutsches Elektronen-Synchrotron DESY.
"""

from systemrdl.rdltypes import AccessType

import _vhdl_templates as _vhdlt
from _hectare_types import AddressMap, Field, Register


class HectareVhdlGen:
    def __init__(self, addrmap):
        self.addrmap = addrmap
        self.cur_indent = 0
        self.data_w_bytes = 4  # 32 / 8  # TODO check

    def generate_string(self):
        # TODO: add header
        s = ""

        s += "entity x is\n"
        s += "  port (\n"
        s += "\n".join(self._gen_ports())
        s += _vhdlt.VHDL_PORTS_AXI
        s += "\n);\n"
        s += "end entity;"

        s += "\n\n# address constants\n"
        s += "\n".join(self._gen_reg_addr())

        s += "\n\n# field ranges constants\n"
        s += "\n".join(self._gen_field_ranges())

        s += "\n\n# registers\n"
        s += "\n".join(self._gen_regs())

        s += _vhdlt.VHDL_INTERNAL_SIG_DEFS

        s += "\n\nbegin\n\n"

        s += "\n".join(self._gen_hw_access())

        s += _vhdlt.VHDL_FSM_READ

        return s

    def _gen_ports(self):
        ports = []
        for reg in self.addrmap.regs:
            for field in reg.fields:
                ports.extend(self._gen_single_port(reg.name, field))
        return ports

    def _gen_reg_addr(self):
        return [
            self._gen_single_addr(reg, self.data_w_bytes) for reg in self.addrmap.regs
        ]

    def _gen_field_ranges(self):
        field_ranges = []
        for reg in self.addrmap.regs:
            for field in reg.fields:
                field_ranges.extend(self._gen_single_field_range(reg.name, field))

        return field_ranges

    def _gen_regs(self):
        return [
            self._gen_single_reg(reg, self.data_w_bytes) for reg in self.addrmap.regs
        ]

    def _gen_hw_access(self):
        hw_access_exprs = []
        for reg in self.addrmap.regs:
            for field in reg.fields:
                hw_access_exprs.extend(self._gen_single_hw_access(reg.name, field))

        return hw_access_exprs

    @staticmethod
    def _gen_single_addr(reg: Register, data_w_bytes: int):
        """ Generate an address constant for a single register

        E.g. constant C_ADDR_SCRATCH : integer := 3;
        """

        word_addr = reg.addr / data_w_bytes
        assert word_addr.is_integer(), (
            "Address should be aligned to data width (%d bytes)" % data_w_bytes
        )
        word_addr = int(word_addr)

        return "constant C_ADDR_{name} : integer := {word_addr};".format(
            name=reg.name.upper(), word_addr=word_addr
        )

    @staticmethod
    def _gen_single_field_range(reg_name: str, field: Field) -> list:
        return [
            "constant C_FIELD_{reg_name}_{field_name}_MSB : integer := {msb};".format(
                reg_name=reg_name.upper(), field_name=field.name.upper(), msb=field.msb
            ),
            "constant C_FIELD_{reg_name}_{field_name}_LSB : integer := {lsb};".format(
                reg_name=reg_name.upper(), field_name=field.name.upper(), lsb=field.lsb
            ),
        ]

    @staticmethod
    def _gen_single_reg(reg: Register, data_w_bytes: int):
        """ signal reg_scratch : std_logic_vector(31 downto 0); """

        return "signal reg_{name} : std_logic_vector({w}-1 downto 0);".format(
            name=reg.name.lower(), w=data_w_bytes * 8
        )

    @staticmethod
    def _gen_single_port(reg_name: str, field: Field) -> list:
        """

        Several possible cases: no access, HW only read, HW only write, HW r/w
        """

        # TODO: if msb == lsb, generate std_logic

        l = []

        assert (
            field.hw_acc_type != AccessType.rw1 or field.hw_acc_type != AccessType.w1
        ), '"rw1" and "w1" are not supported for HW access'

        if field.hw_acc_type == AccessType.r or field.hw_acc_type == AccessType.rw:
            out_str = "{reg_name}_{field_name}_o : out std_logic_vector({msb} downto {lsb});".format(
                field_name=field.name.lower(),
                reg_name=reg_name.lower(),
                msb=field.msb,
                lsb=field.lsb,
            )
            l.append(out_str)

        if field.hw_acc_type == AccessType.w or field.hw_acc_type == AccessType.rw:
            in_str = "{reg_name}_{field_name}_i : in std_logic_vector({msb} downto {lsb});".format(
                field_name=field.name.lower(),
                reg_name=reg_name.lower(),
                msb=field.msb,
                lsb=field.lsb,
            )
            l.append(in_str)

        return l

    @staticmethod
    def _gen_single_hw_access(reg_name: str, field: Field, in_reg=True) -> list:
        """

        Several possible cases: no access, HW only read, HW only write, HW r/w
        """

        # TODO: register generation for output
        # TODO: if msb == lsb, generate std_logic
        # TODO: somewhere handle write enable

        l = []

        assert (
            field.hw_acc_type != AccessType.rw1 or field.hw_acc_type != AccessType.w1
        ), '"rw1" and "w1" are not supported for HW access'

        if field.hw_acc_type == AccessType.r or field.hw_acc_type == AccessType.rw:
            out_str = "{reg_name}_{field_name}_o <= reg_{reg_name}({msb} downto {lsb});".format(
                field_name=field.name.lower(),
                reg_name=reg_name.lower(),
                msb=field.msb,
                lsb=field.lsb,
            )
            l.append(out_str)

        if field.hw_acc_type == AccessType.w or field.hw_acc_type == AccessType.rw:
            update_cond = " when rising_edge(clk)" if in_reg else ""
            in_str = "reg_{reg_name}({msb} downto {lsb}) <= {reg_name}_{field_name}_i{update_cond};".format(
                field_name=field.name.lower(),
                reg_name=reg_name.lower(),
                msb=field.msb,
                lsb=field.lsb,
                update_cond=update_cond,
            )
            l.append(in_str)

        return l
