#===============================================================================
# delete old files

if {[file exists work]} {
    vdel -lib work -all
}

#===============================================================================
# compile modules

vlib work

# DUT
vcom ../hdl/mymodule_pkg.vhd
vcom ../hdl/mymodule.vhd

# TB
vcom -2008 ../tb/mymodule_th.vhd
vcom -2008 ../tb/mymodule_tb.vhd

#===============================================================================
# start the simulation

vsim work.mymodule_tb

add wave -divider "Clock and reset"
add wave \
    sim:/mymodule_tb/inst_test_harness/clk \
    sim:/mymodule_tb/inst_test_harness/reset

add wave -divider "AXI"
add wave -radix hex  \
    sim:/mymodule_tb/inst_test_harness/S_AXI_AWADDR \
    sim:/mymodule_tb/inst_test_harness/S_AXI_AWPROT \
    sim:/mymodule_tb/inst_test_harness/S_AXI_AWVALID \
    sim:/mymodule_tb/inst_test_harness/S_AXI_AWREADY \
    sim:/mymodule_tb/inst_test_harness/S_AXI_WDATA \
    sim:/mymodule_tb/inst_test_harness/S_AXI_WSTRB \
    sim:/mymodule_tb/inst_test_harness/S_AXI_WVALID \
    sim:/mymodule_tb/inst_test_harness/S_AXI_WREADY \
    sim:/mymodule_tb/inst_test_harness/S_AXI_BRESP \
    sim:/mymodule_tb/inst_test_harness/S_AXI_BVALID \
    sim:/mymodule_tb/inst_test_harness/S_AXI_BREADY \
    sim:/mymodule_tb/inst_test_harness/S_AXI_ARADDR \
    sim:/mymodule_tb/inst_test_harness/S_AXI_ARPROT \
    sim:/mymodule_tb/inst_test_harness/S_AXI_ARVALID \
    sim:/mymodule_tb/inst_test_harness/S_AXI_ARREADY \
    sim:/mymodule_tb/inst_test_harness/S_AXI_RDATA \
    sim:/mymodule_tb/inst_test_harness/S_AXI_RRESP \
    sim:/mymodule_tb/inst_test_harness/S_AXI_RVALID \
    sim:/mymodule_tb/inst_test_harness/S_AXI_RREADY

add wave -divider "logic"
add wave -radix unsigned \
    sim:/mymodule_tb/inst_test_harness/coef_a_a_o \
    sim:/mymodule_tb/inst_test_harness/coef_b_b_o \
    sim:/mymodule_tb/inst_test_harness/result_sum_i \
    sim:/mymodule_tb/inst_test_harness/result_diff_i

add wave -divider "DUT - internal"

add wave -radix unsigned \
    sim:/mymodule_tb/inst_test_harness/inst_dut/waddr_word \
    sim:/mymodule_tb/inst_test_harness/inst_dut/raddr_word

add wave -radix hex \
    sim:/mymodule_tb/inst_test_harness/inst_dut/reg_result \
    sim:/mymodule_tb/inst_test_harness/inst_dut/rdata_reg

add wave -divider "enums"

add wave \
    sim:/mymodule_tb/inst_test_harness/control_color_sel_o \
    sim:/mymodule_tb/inst_test_harness/control_color_sel_swmod \
    sim:/mymodule_tb/inst_test_harness/status_color_sel_rbv_i


#===============================================================================
# run until the end

run -all

wave zoom full
