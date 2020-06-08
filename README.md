# HECTARE - Hamburg Elegant CreaTor from Accellera™ systemrdl™ to REgisters

This is a tool which generates AXI4-Lite slave from a description in
[SystemRDL](https://www.accellera.org/activities/working-groups/systemrdl).

It uses [systemrdl-compiler](https://github.com/SystemRDL/systemrdl-compiler)
as a front end and a custom backend to generate a VHDL module.

The HECTARE tool is developed by [MicroTCA Tech Lab](https://techlab.desy.de/)
at DESY.

## Usage

```
$ hectare.py --help
usage: hectare.py [-h] [--debug] [--axi-vhdl VHDL_NAME] filename

HECTARE - Hamburg Elegant CreaTor from Accelera systemrdl to REgisters

positional arguments:
  filename              .rdl file

optional arguments:
  -h, --help            show this help message and exit
  --debug               enable debugging information
  --axi-vhdl VHDL_NAME  generate AXI4-Lite slave
```

## Useful arguments

  * `sw`: `r`, `rw`, `w`, `na`
  * `hw`: `r`, `rw`, `w`, `na`
  * `swmod`
  * `singlepulse` (currently not yet supported)
  * `encode`

## Changelog

### [0.2.0] - 2020-06-08

* First public release
* Provides generation of AXI4-Lite module in VHDL
* Supports all possible combination for `sw` and `rw` properties as well as
  `swmod` and `encode` attribute

## Tests

Several tests are provided in `test` folder

### 00_unit_test

This is a simple unit test based on the Python [] framework.

### 01_uvvm_simple

**UVVM version: v2019.12.04**

Regenerating the output products (in shell, from folder `hdl`):

```
$ ./gen_output.sh
Parsing finished.
generate_package
Generating mymodule.vhd ...
Generating mymodule_pkg.vhd ...
Done.
```

Running the test (in ModelSim, from folder `work`)

```
do ../scripts/compile_uvvm.do
do ../scripts/sim.do
```

### 02_hdlparse

Requires **hdlparse** from a fork (the one from pip is missing some features)
available from https://github.com/andresmanelli/hdlparse on branch `entity`.

### 03_ordt_equivalence

Compares the output of HECTARE against Juniper®
[ordt](https://github.com/Juniper/open-register-design-tool).

Alias to `ordt` should be created, as explained
[here](https://github.com/Juniper/open-register-design-tool/wiki/Running-Ordt).

---

Accellera™ and SystemRDL™ are trademarks of Accellera Systems Initiative Inc.

Juniper® is a registered trademark of Juniper Networks, Inc.
