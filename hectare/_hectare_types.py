"""
Copyright (c) 2020 Deutsches Elektronen-Synchrotron DESY.
"""


class AddressMap:
    def __init__(self, name):
        self.name = name
        self.regs = []


class Register:
    def __init__(self, name, addr):
        self.name = name
        self.addr = addr
        self.fields = []


class Field:
    def __init__(self, name, lsb, msb, hw_acc_type, sw_acc_type):
        self.name = name
        self.lsb = lsb
        self.msb = msb
        self.hw_acc_type = hw_acc_type
        self.sw_acc_type = sw_acc_type
