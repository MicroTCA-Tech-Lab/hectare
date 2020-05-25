"""
Copyright (c) 2020 Deutsches Elektronen-Synchrotron DESY.
"""

import datetime
import getpass
import os
import socket

from systemrdl.rdltypes import AccessType

import _vhdl_templates as _vhdlt
from _hectare_types import AddressMap, Field, Register


class HectareVhdlGen:
    def __init__(self, addrmap):
        self.addrmap = addrmap
        self.cur_indent = 0
        self.data_w_bytes = 4  # 32 / 8  # TODO check regwidth

    def generate_string(self):
        s = ""

        s += self._gen_header()

        s += _vhdlt.VHDL_LIBS
        s += "\n"

        s += "entity {entity_name} is\n".format(entity_name=self.addrmap.name)
        s += "  generic(\n"
        s += "    G_ADDR_W: integer := 8\n"
        s += "  );\n"
        s += "  port (\n"
        s += "\n".join(self._gen_ports())
        s += _vhdlt.VHDL_PORTS_AXI
        s += "\n);\n"
        s += "end entity;\n\n"

        s += "architecture arch of {entity_name} is\n".format(
            entity_name=self.addrmap.name
        )

        s += "\n\n-- address constants\n"
        s += "\n".join(self._gen_reg_addr())

        s += "\n\n-- field ranges constants\n"
        s += "\n".join(self._gen_field_ranges())

        s += "\n\n-- registers\n"
        s += "\n".join(self._gen_regs())

        s += _vhdlt.VHDL_INTERNAL_SIG_DEFS

        s += "\n\nbegin\n\n"

        s += "\n".join(self._gen_hw_access())

        s += _vhdlt.VHDL_FSM_READ

        s += "\n\n  -- ### read logic\n\n"
        s += "\n".join(self._gen_read_logic())
        s += "\n"

        s += _vhdlt.VHDL_FSM_WRITE

        s += "  -- ### write logic (use waddr_word and wdata_reg)\n\n"
        s += "\n".join(self._gen_write_logic())

        s += _vhdlt.VHDL_WRITE_OUTPUT
        s += _vhdlt.VHDL_END_ARCH

        return s

    @staticmethod
    def _gen_header() -> str:
        s = "-- This file was automatically generated with HECTARE\n"
        s += "--\n"
        s += "-- DO NOT EDIT\n"
        # TODO: add original file name
        s += "--\n"
        s += "--   date     = {0}\n".format(datetime.datetime.now().ctime())
        s += "--   hostname = {0}\n".format(socket.gethostname())
        s += "--   user     = {0}\n".format(getpass.getuser())
        s += "\n"
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

    def _gen_hw_access(self) -> list:
        hw_access_exprs = []
        for reg in self.addrmap.regs:
            for field in reg.fields:
                hw_access_exprs.extend(self._gen_single_hw_access(reg.name, field))

        return hw_access_exprs

    def _gen_read_logic(self) -> list:
        lines = []

        lines.append("  proc_rdata_reg: process (clk)")
        lines.append("  begin")
        lines.append("    if rising_edge(clk) then")
        lines.append("      rdata_reg <= (others => '0');")
        lines.append("      case raddr_word is")
        for reg in self.addrmap.regs:
            lines.append("        when C_ADDR_{0} =>".format(reg.name.upper()))
            reg_has_assign = False
            for field in reg.fields:
                line = self._gen_single_sw_rd_access(reg.name, field)
                if line is not None:
                    lines.append("          " + line)
                    reg_has_assign = True

            if not reg_has_assign:
                lines.append("          null;")

        lines.append("        when others  =>")
        lines.append("          null;")
        lines.append("      end case;")
        lines.append("    end if;")
        lines.append("  end process;")
        return lines

    def _gen_write_logic(self) -> list:
        lines = []
        lines.append("proc_write: process (clk) begin")
        lines.append("  if rising_edge(clk) then")
        lines.append("")
        lines.append("    -- default (TODO)")
        # TODO: handle here pulses
        lines.append("")

        lines.append(
            "    if state_write = sWriteResp and state_write_prev /= sWriteResp then"
        )
        lines.append("      case waddr_word is")

        for reg in self.addrmap.regs:
            lines.append("        when C_ADDR_{0} =>".format(reg.name.upper()))
            reg_has_assign = False
            for field in reg.fields:
                line = self._gen_single_sw_wr_access(reg.name, field)
                if line is not None:
                    lines.append("          " + line)
                    reg_has_assign = True

            if not reg_has_assign:
                lines.append("          null;")

        lines.append("        when others  =>")
        lines.append("          null;")
        lines.append("      end case;")
        lines.append("    end if;")
        lines.append("  end if;")
        lines.append("end process;")

        return lines

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
                msb=field.msb - field.lsb,
                lsb=0,
            )
            l.append(out_str)

        if field.hw_acc_type == AccessType.w or field.hw_acc_type == AccessType.rw:
            in_str = "{reg_name}_{field_name}_i : in std_logic_vector({msb} downto {lsb});".format(
                field_name=field.name.lower(),
                reg_name=reg_name.lower(),
                msb=field.msb - field.lsb,
                lsb=0,
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

    @staticmethod
    def _gen_single_sw_rd_access(reg_name: str, field: Field):
        """

        Several possible cases: no access, SW only read, SW only write, SW r/w

        reg_idelay_inc(8 downto 0) <= wdata_reg(8 downto 0);
        """

        # TODO: mypy None or str

        assert (
            field.sw_acc_type != AccessType.rw1 or field.sw_acc_type != AccessType.w1
        ), '"rw1" and "w1" are not supported for HW access'

        if field.sw_acc_type == AccessType.r or field.sw_acc_type == AccessType.rw:
            out_str = "rdata_reg({msb} downto {lsb}) <= reg_{reg_name}({msb} downto {lsb});".format(
                field_name=field.name.lower(),
                reg_name=reg_name.lower(),
                msb=field.msb,
                lsb=field.lsb,
            )
            return out_str

        return None

    @staticmethod
    def _gen_single_sw_wr_access(reg_name: str, field: Field):
        """

        Several possible cases: no access, SW only read, SW only write, SW r/w

        reg_idelay_inc(8 downto 0) <= wdata_reg(8 downto 0);
        """

        # TODO: mypy None or str

        assert (
            field.sw_acc_type != AccessType.rw1 or field.sw_acc_type != AccessType.w1
        ), '"rw1" and "w1" are not supported for HW access'

        if field.sw_acc_type == AccessType.w or field.sw_acc_type == AccessType.rw:
            in_str = "reg_{reg_name}({msb} downto {lsb}) <= wdata_reg({msb} downto {lsb});".format(
                field_name=field.name.lower(),
                reg_name=reg_name.lower(),
                msb=field.msb,
                lsb=field.lsb,
            )
            return in_str

        return None
