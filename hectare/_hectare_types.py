"""
Copyright (c) 2020 Deutsches Elektronen-Synchrotron DESY.

See LICENSE.txt for license details.
"""

import enum
from typing import Dict, List, Optional, Set, Tuple

import systemrdl


class AddressMap:
    def __init__(self, name: str):
        self.name = name
        self.regs: List[Register] = []


class Register:
    def __init__(self, name: str, addr: int):
        self.name: str = name
        self.addr: int = addr
        self.fields: List[Field] = []


class Field:
    def __init__(
        self,
        name: str,
        lsb: int,
        msb: int,
        hw_acc_type: systemrdl.rdltypes.AccessType,
        sw_acc_type: systemrdl.rdltypes.AccessType,
        swmod: bool,
        encode: Optional[enum.EnumMeta] = None,
        reset: Optional[int] = None,
    ):
        self.name: str = name
        self.lsb: int = lsb
        self.msb: int = msb
        self.hw_acc_type: systemrdl.rdltypes.AccessType = hw_acc_type
        self.sw_acc_type: systemrdl.rdltypes.AccessType = sw_acc_type
        self.swmod: bool = swmod
        self.encode = encode
        self.reset: Optional[int] = reset
