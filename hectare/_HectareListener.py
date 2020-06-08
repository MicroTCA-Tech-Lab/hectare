"""
Copyright (c) 2020 Deutsches Elektronen-Synchrotron DESY.

See LICENSE.txt for license details.
"""

import logging

from systemrdl import RDLListener
from systemrdl.node import FieldNode, RegNode

from hectare._hectare_types import AddressMap, Field, Register


class HectareListener(RDLListener):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.cur_addrmap = None
        self.cur_reg = None
        self.addrmaps = []

    def enter_Addrmap(self, node):
        self.logger.debug("Entering addrmap, node = %s", node.get_path())
        self.cur_addrmap = AddressMap(node.inst_name)

    def exit_Addrmap(self, node):
        self.logger.debug("Exiting addrmap, node = %s", node.get_path())
        self.addrmaps.append(self.cur_addrmap)

    def enter_Reg(self, node):
        self.logger.debug("Entering register, node = %s", node.get_path())
        # has_sw_readable, has_sw_writable
        self.cur_reg = Register(node.inst_name, node.address_offset)

    def exit_Reg(self, node):
        self.logger.debug("Exiting register, node = %s", node.get_path())
        self.cur_addrmap.regs.append(self.cur_reg)

    def enter_Field(self, node):
        self.logger.debug("Entering field, node = %s", node.get_path())

        assert isinstance(
            node, FieldNode
        ), "This program expects that registers only contain fields"

        self.cur_reg.fields.append(
            Field(
                node.inst_name,
                node.lsb,
                node.msb,
                sw_acc_type=node.get_property("sw"),
                hw_acc_type=node.get_property("hw"),
                swmod=node.get_property("swmod"),
                encode=node.get_property("encode"),
                reset=node.get_property("reset"),
            )
        )

    def exit_Field(self, node):
        self.logger.debug("Exiting field, node = %s", node.get_path())
