"""
Copyright (c) 2020 Deutsches Elektronen-Synchrotron DESY.

See LICENSE.txt for license details.
"""

import datetime
import getpass
import os
import socket
from typing import Iterator, List, Optional

from systemrdl.rdltypes import AccessType

import hectare._vhdl_templates as _vhdlt
from hectare._hectare_types import AddressMap, Field, Register


def indent_lines(ls: List[str], ident_level: int) -> Iterator[str]:
    for l in ls:
        yield " " * ident_level + l


class HectareVhdlGen:
    def __init__(self, addrmap, input_filename=""):
        self.addrmap = addrmap
        self.cur_indent = 0
        self.data_w_bytes = 4  # 32 / 8  # TODO check regwidth
        self.input_filename = input_filename

    def generate_package(self) -> Optional[str]:
        """ generates package with VHDL enums if the register description
        contains enums
        """

        print("generate_package")

        # first check if any fields are enum, otherwise package is not generated
        lines = []
        generated_enums = set()

        for reg in self.addrmap.regs:
            for field in reg.fields:
                if field.encode is not None and field.encode not in generated_enums:
                    lines.extend(self._gen_single_enum_type(field))
                    lines.append("")
                    generated_enums.add(field.encode)

        if lines:
            # at least one enum was found, generated package string

            s = ""
            s += self._gen_header(self.input_filename)
            s += _vhdlt.VHDL_LIBS
            s += "\n"

            s += "package {entity_name}_pkg is\n".format(entity_name=self.addrmap.name)
            s += "\n"
            s += "  -- attributes\n"
            s += "  attribute enum_encoding: string;\n"
            s += "\n"

            for line in lines:
                s += "  " + line + "\n"

            s += "\n"
            s += "end package;\n"

            return s

    def generate_string(self) -> str:
        s = ""

        s += self._gen_header(self.input_filename)

        s += _vhdlt.VHDL_LIBS
        s += "\n"

        # check if there is package being generated, add package to the includes
        contains_enums = False
        for reg in self.addrmap.regs:
            for field in reg.fields:
                if field.encode is not None:
                    contains_enums = True

        if contains_enums:
            s += "use work.{entity_name}_pkg.all;\n".format(
                entity_name=self.addrmap.name
            )
            s += "\n"

        s += "entity {entity_name}_axi is\n".format(entity_name=self.addrmap.name)
        s += "  generic(\n"
        s += "    G_ADDR_W: integer := 8\n"
        s += "  );\n"
        s += "  port (\n"
        s += "\n".join(indent_lines(self._gen_ports(), 4))
        s += "\n"
        s += _vhdlt.VHDL_PORTS_AXI
        s += "\n);\n"
        s += "end entity;\n\n"

        s += "architecture arch of {entity_name}_axi is\n".format(
            entity_name=self.addrmap.name
        )

        s += "\n\n  -- address constants\n"
        s += "\n".join(indent_lines(self._gen_reg_addr(), 2))

        s += "\n\n  -- field ranges constants\n"
        s += "\n".join(indent_lines(self._gen_field_ranges(), 2))

        s += "\n\n  -- registers\n"
        s += "\n".join(indent_lines(self._gen_regs(), 2))
        s += "\n\n"

        s += _vhdlt.VHDL_INTERNAL_SIG_DEFS

        s += "\n\nbegin\n\n"

        s += "\n".join(indent_lines(self._gen_hw_access(), 2))

        s += "\n\n\n"
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
    def _gen_header(input_filename: str, verbose: bool = False) -> str:
        s = "-- This file was automatically generated with HECTARE\n"
        s += "--\n"
        s += "-- DO NOT EDIT\n"
        s += "--\n"
        s += "--   input_filename = {0}\n".format(input_filename)
        if verbose:
            s += "--   date     = {0}\n".format(datetime.datetime.now().ctime())
            s += "--   hostname = {0}\n".format(socket.gethostname())
            s += "--   user     = {0}\n".format(getpass.getuser())
        s += "\n"
        return s

    def _gen_ports(self) -> List[str]:
        ports = []
        for reg in self.addrmap.regs:
            for field in reg.fields:
                ports.extend(self._gen_single_port(reg.name, field))
        return ports

    def _gen_reg_addr(self) -> List[str]:
        return [
            self._gen_single_addr(reg, self.data_w_bytes) for reg in self.addrmap.regs
        ]

    def _gen_field_ranges(self) -> List[str]:
        field_ranges = []
        for reg in self.addrmap.regs:
            for field in reg.fields:
                field_ranges.extend(self._gen_single_field_range(reg.name, field))

        return field_ranges

    def _gen_regs(self) -> List[str]:
        ls = [self._gen_single_reg(reg, self.data_w_bytes) for reg in self.addrmap.regs]
        for reg in self.addrmap.regs:
            swmod_reg = self._gen_single_reg_swmod(reg, self.data_w_bytes)
            if swmod_reg is not None:
                ls.append(swmod_reg)
        return ls

    def _gen_hw_access(self) -> List[str]:
        hw_access_exprs = []
        for reg in self.addrmap.regs:
            for field in reg.fields:
                hw_access_exprs.extend(self._gen_single_hw_access(reg.name, field))

        return hw_access_exprs

    def _gen_read_logic(self) -> List[str]:
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

    def _gen_write_logic(self) -> List[str]:
        lines = []
        lines.append("proc_write: process (clk) begin")
        lines.append("  if rising_edge(clk) then")
        lines.append("    if reset = '1' then")

        # generate reset assignments
        for reg in self.addrmap.regs:
            for field in reg.fields:
                line = self._gen_single_reset_assignment(reg.name, field)
                if line is not None:
                    lines.append("      " + line)

        lines.append("    else")
        lines.append("")
        lines.append("      -- default (pulse)")
        lines.append("      -- TODO")
        # TODO: handle here pulses
        lines.append("")
        lines.append("      -- default (swmod)")
        for reg in self.addrmap.regs:
            has_swmod = any(map(lambda f: f.swmod, reg.fields))
            if has_swmod:
                lines.append(
                    "      reg_{name}_swmod <= '0';".format(name=reg.name.lower())
                )

        lines.append("")

        lines.append(
            "      if state_write = sWriteResp and state_write_prev /= sWriteResp then"
        )
        lines.append("        case waddr_word is")

        for reg in self.addrmap.regs:
            lines.append("          when C_ADDR_{0} =>".format(reg.name.upper()))
            reg_has_assign = False
            for field in reg.fields:
                line = self._gen_single_sw_wr_access(reg.name, field)
                if line is not None:
                    lines.append("            " + line)
                    reg_has_assign = True
                # swmod
                has_swmod = any(map(lambda f: f.swmod, reg.fields))
                if has_swmod:
                    lines.append(
                        "            reg_{name}_swmod <= '1';".format(
                            name=reg.name.lower()
                        )
                    )

            if not reg_has_assign:
                lines.append("            null;")

        lines.append("          when others  =>")
        lines.append("            null;")
        lines.append("        end case;")
        lines.append("      end if;")
        lines.append("    end if;")
        lines.append("  end if;")
        lines.append("end process;")

        return lines

    @staticmethod
    def _gen_single_enum_type(field: Field) -> str:
        assert (
            field.encode is not None
        ), "_gen_single_enum_type should only be called on enums"

        # right now we only support enums which start at 0 and are sequential
        do_vals_start_at_zero_and_inc_by_1 = all(
            map(
                lambda ab: ab[0] == ab[1],
                enumerate(map(lambda it: it.value, field.encode)),
            )
        )
        assert (
            do_vals_start_at_zero_and_inc_by_1
        ), "only supported encoding are those who start at 0 and increment by 1"

        lines = []
        lines.append(
            "type {encode_name}_t is (".format(encode_name=field.encode.__name__)
        )
        for item in field.encode:
            lines.append("  " + item.name + ",")

        # last line has also a ",", which needs to be removed
        lines[-1] = lines[-1][:-1]

        lines.append(");")
        return lines

    @staticmethod
    def _gen_single_addr(reg: Register, data_w_bytes: int) -> str:
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
    def _gen_single_field_range(reg_name: str, field: Field) -> List[str]:
        return [
            "constant C_FIELD_{reg_name}_{field_name}_MSB : integer := {msb};".format(
                reg_name=reg_name.upper(), field_name=field.name.upper(), msb=field.msb
            ),
            "constant C_FIELD_{reg_name}_{field_name}_LSB : integer := {lsb};".format(
                reg_name=reg_name.upper(), field_name=field.name.upper(), lsb=field.lsb
            ),
        ]

    @staticmethod
    def _gen_single_reg(reg: Register, data_w_bytes: int) -> str:
        """ signal reg_scratch : std_logic_vector(31 downto 0); """

        return "signal reg_{name} : std_logic_vector({w}-1 downto 0);".format(
            name=reg.name.lower(), w=data_w_bytes * 8
        )

    @staticmethod
    def _gen_single_reg_swmod(reg: Register, data_w_bytes: int) -> Optional[str]:
        """ generates swmod reg is at least one field in the register has swmod attribute  """

        has_swmod = any(map(lambda f: f.swmod, reg.fields))
        if has_swmod:
            return "signal reg_{name}_swmod : std_logic;".format(name=reg.name.lower())
        else:
            return None

    @staticmethod
    def _gen_single_port(reg_name: str, field: Field) -> List[str]:
        """ Generate output and input ports for a single field

        Several possible cases: no access, HW only read, HW only write, HW r/w.
        Also handles swmod attribute, by generating additional _swmod output
        """

        l = []

        assert (
            field.hw_acc_type != AccessType.rw1 or field.hw_acc_type != AccessType.w1
        ), '"rw1" and "w1" are not supported for HW access'

        if field.encode is not None:
            port_type = "{encode_name}_t".format(encode_name=field.encode.__name__)
        elif field.msb == field.lsb:
            port_type = "std_logic"
        else:
            port_type = "std_logic_vector({msb} downto {lsb})".format(
                msb=field.msb - field.lsb, lsb=0
            )

        if field.hw_acc_type == AccessType.r or field.hw_acc_type == AccessType.rw:
            out_str = "{reg_name}_{field_name}_o : out {port_type};".format(
                field_name=field.name.lower(),
                reg_name=reg_name.lower(),
                port_type=port_type,
            )
            l.append(out_str)

        if field.hw_acc_type == AccessType.w or field.hw_acc_type == AccessType.rw:
            in_str = "{reg_name}_{field_name}_i : in {port_type};".format(
                field_name=field.name.lower(),
                reg_name=reg_name.lower(),
                port_type=port_type,
            )
            l.append(in_str)

        if field.swmod:
            swmod_str = "{reg_name}_{field_name}_swmod : out std_logic;".format(
                field_name=field.name.lower(), reg_name=reg_name.lower()
            )
            l.append(swmod_str)

        return l

    @staticmethod
    def _gen_single_hw_access(reg_name: str, field: Field, in_reg=True) -> List[str]:
        """

        - Several possible cases: no access, HW only read, HW only write, HW r/w
        - if the field is enum, convert from slv to enum for outputs, and from
          enum to slv for inputs

        """

        # TODO: somewhere handle write enable

        l = []

        assert (
            field.hw_acc_type != AccessType.rw1 or field.hw_acc_type != AccessType.w1
        ), '"rw1" and "w1" are not supported for HW access'

        reg_slice = (
            "{msb}".format(msb=field.msb)
            if field.msb == field.lsb
            else "{msb} downto {lsb}".format(msb=field.msb, lsb=field.lsb,)
        )

        if field.encode is None:
            enum_conv_out_left = ""
            enum_conv_out_right = ""
            enum_conv_in_left = ""
            enum_conv_in_right = ""
        else:
            enum_conv_out_left = "{encode_name}_t'val(to_integer(unsigned(".format(
                encode_name=field.encode.__name__
            )
            enum_conv_out_right = ")))"
            enum_conv_in_left = "std_logic_vector(to_unsigned({encode_name}_t'pos(".format(
                encode_name=field.encode.__name__
            )
            enum_conv_in_right = "), {field_length}))".format(
                field_length=field.msb - field.lsb + 1
            )

        if field.hw_acc_type == AccessType.r or field.hw_acc_type == AccessType.rw:
            out_str = "{reg_name}_{field_name}_o <= {enum_conv_out_left}reg_{reg_name}({reg_slice}){enum_conv_out_right};".format(
                field_name=field.name.lower(),
                reg_name=reg_name.lower(),
                reg_slice=reg_slice,
                enum_conv_out_left=enum_conv_out_left,
                enum_conv_out_right=enum_conv_out_right,
            )
            l.append(out_str)

        if field.hw_acc_type == AccessType.w or field.hw_acc_type == AccessType.rw:
            update_cond = " when rising_edge(clk)" if in_reg else ""
            in_str = "reg_{reg_name}({reg_slice}) <= {enum_conv_in_left}{reg_name}_{field_name}_i{enum_conv_in_right}{update_cond};".format(
                field_name=field.name.lower(),
                reg_name=reg_name.lower(),
                reg_slice=reg_slice,
                update_cond=update_cond,
                enum_conv_in_left=enum_conv_in_left,
                enum_conv_in_right=enum_conv_in_right,
            )
            l.append(in_str)

        if field.swmod:
            swmod_str = "{reg_name}_{field_name}_swmod <= reg_{reg_name}_swmod;".format(
                field_name=field.name.lower(), reg_name=reg_name.lower(),
            )
            l.append(swmod_str)

        return l

    @staticmethod
    def _gen_single_sw_rd_access(reg_name: str, field: Field) -> Optional[str]:
        """

        Several possible cases: no access, SW only read, SW only write, SW r/w

        reg_idelay_inc(8 downto 0) <= wdata_reg(8 downto 0);
        """

        assert (
            field.sw_acc_type != AccessType.rw1 or field.sw_acc_type != AccessType.w1
        ), '"rw1" and "w1" are not supported for HW access'

        if field.sw_acc_type == AccessType.r or field.sw_acc_type == AccessType.rw:
            out_str = "rdata_reg({msb} downto {lsb}) <= reg_{reg_name}({msb} downto {lsb});".format(
                reg_name=reg_name.lower(), msb=field.msb, lsb=field.lsb,
            )
            return out_str

        return None

    @staticmethod
    def _gen_single_sw_wr_access(reg_name: str, field: Field) -> Optional[str]:
        """

        Several possible cases: no access, SW only read, SW only write, SW r/w

        reg_idelay_inc(8 downto 0) <= wdata_reg(8 downto 0);
        """

        assert (
            field.sw_acc_type != AccessType.rw1 or field.sw_acc_type != AccessType.w1
        ), '"rw1" and "w1" are not supported for HW access'

        if field.sw_acc_type == AccessType.w or field.sw_acc_type == AccessType.rw:
            in_str = "reg_{reg_name}({msb} downto {lsb}) <= wdata_reg({msb} downto {lsb});".format(
                reg_name=reg_name.lower(), msb=field.msb, lsb=field.lsb,
            )
            return in_str

        return None

    @staticmethod
    def _gen_single_reset_assignment(reg_name: str, field: Field) -> Optional[str]:
        """ Generate reset assignment if the field has a reset value """

        if field.reset is not None:
            msb = field.msb
            lsb = field.lsb

            # we always assign to a vector, even for single-bit signals
            assign_val = '"{val:0{l}b}"'.format(val=field.reset, l=msb - lsb + 1)

            assign_str = "reg_{reg_name}({msb} downto {lsb}) <= {assign_val};".format(
                reg_name=reg_name.lower(), msb=msb, lsb=lsb, assign_val=assign_val
            )
            return assign_str

        return None
