# HECTARE - Hamburg Elegant CreaTor from Accellera™ systemrdl™ to REgisters

This is a tool which generates AXI4-Lite slave from a description in
[SystemRDL](https://www.accellera.org/activities/working-groups/systemrdl).

It uses [systemrdl-compiler](https://github.com/SystemRDL/systemrdl-compiler)
as a front end and a custom backend to generate a VHDL module.

## Usage



## Tests

Several tests are provided in `test` folder

### 00_unit_test

This is a simple unit test based on the Python [] framework.

### 01_uvvm_simple

**UVVM version: v2019.12.04**

Running the test (from folder `work`)

```
do ../scripts/compile_uvvm.do
../../../hectare/hectare.py ../hdl/mymodule.rdl
do ../scripts/sim.do
```

---

Accellera™ and SystemRDL™ are  trademarks of Accellera Systems Initiative Inc.
