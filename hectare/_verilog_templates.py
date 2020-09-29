"""
Copyright (c) 2020 Deutsches Elektronen-Synchrotron DESY.

See LICENSE.txt for license details.
"""
#
# Given that this is machine-generated code, we use the lowest common subset,
# i.e. Verilog 2001.
# We could use nicer SV but there are enough tools not supporting it, that using
# if for machine generated code is pointless
#
VERILOG_LIBS = """
//library ieee;
//use ieee.std_logic_1164.all;
//use ieee.numeric_std.all;
"""

VERILOG_PORTS_AXI = """
    input               clk,
    input               reset,
    input [G_ADDR_W-1:0]S_AXI_AWADDR,
    input          [2:0]S_AXI_AWPROT,
    input               S_AXI_AWVALID,
    output              S_AXI_AWREADY,
    input         [31:0]S_AXI_WDATA,
    input     [32/8-1:0]S_AXI_WSTRB,
    input               S_AXI_WVALID,
    output              S_AXI_WREADY,
    output         [1:0]S_AXI_BRESP,
    output              S_AXI_BVALID,
    input               S_AXI_BREADY,
    input [G_ADDR_W-1:0]S_AXI_ARADDR,
    input          [2:0]S_AXI_ARPROT,
    input               S_AXI_ARVALID,
    output              S_AXI_ARREADY,
    output        [31:0]S_AXI_RDATA,
    output         [1:0]S_AXI_RRESP,
    output              S_AXI_RVALID,
    input               S_AXI_RREADY
"""

VERILOG_INTERNAL_SIG_DEFS = """
  // read
  `define sReadIdle  1'b0
  `define sReadValid 1'b1
  logic state_read;
  
  logic [31:0]rdata_reg;
  logic [31:0]raddr_word;
  
  logic arready_wire;
  logic rvalid_wire;
  
  // write
  `define sWriteIdle     2'b00
  `define sWriteWaitData 2'b01
  `define sWriteWaitAddr 2'b10
  `define sWriteResp     2'b11
  logic [1:0]state_write;
  logic [1:0]state_write_prev;
  
  logic [G_ADDR_W-1:0]waddr_reg;
  logic         [31:0]wdata_reg;
  
  logic [31:0]waddr_word;
  
  logic awready_wire;
  logic wready_wire;
  logic bvalid_wire;
"""

VERILOG_FSM_READ = """
  always @(posedge clk)
    if (reset)
      state_read <= `sReadIdle;
    else
      case (state_read)
        `sReadIdle:
          if (S_AXI_ARVALID)
            state_read <= `sReadValid;

        `sReadValid:
          if (S_AXI_RREADY)
            state_read <= `sReadIdle;
      endcase

  assign raddr_word = {{(32-(G_ADDR_W-2)){1'b0}}, S_AXI_ARADDR[G_ADDR_W-1:2]};
"""

VERILOG_FSM_WRITE = """
  always @(*)
    case (state_read)
      `sReadIdle:
        begin
          arready_wire = 1'b1;
          rvalid_wire  = 1'b0;
        end
      `sReadValid:
        begin
          arready_wire = 1'b0;
          rvalid_wire  = 1'b1;
        end
      default:
        begin
          arready_wire = 1'b0;
          rvalid_wire  = 1'b0;
        end
    endcase

  assign S_AXI_ARREADY = arready_wire;
  assign S_AXI_RVALID  = rvalid_wire;
  assign S_AXI_RDATA   = rdata_reg;
  assign S_AXI_RRESP   = 2'b00;

  always @(posedge clk)
    state_write_prev <= state_write;

  always @(posedge clk)
    if (reset)
      state_write <= `sWriteIdle;
    else
      case (state_write)
        `sWriteIdle:
          if (S_AXI_AWVALID && S_AXI_WVALID)
          begin
            state_write <= `sWriteResp;
            waddr_reg <= S_AXI_AWADDR;
            wdata_reg <= S_AXI_WDATA;
          end
          else if (S_AXI_AWVALID && !S_AXI_WVALID)
          begin
            state_write <= `sWriteWaitData;
            waddr_reg <= S_AXI_AWADDR;
          end
          else if (!S_AXI_AWVALID && S_AXI_WVALID)
          begin
            state_write <= `sWriteWaitAddr;
            wdata_reg <= S_AXI_WDATA;
          end

        `sWriteWaitData:
          if (S_AXI_WVALID)
          begin
            state_write <= `sWriteResp;
            wdata_reg <= S_AXI_WDATA;
          end

        `sWriteWaitAddr:
          if (S_AXI_AWVALID)
          begin
            state_write <= `sWriteResp;
            waddr_reg <= S_AXI_AWADDR;
          end

        `sWriteResp:
          if (S_AXI_BREADY)
            state_write <= `sWriteIdle;
      endcase

  assign waddr_word = {{(32-(G_ADDR_W-2)){1'b0}}, waddr_reg[G_ADDR_W-1:2]};
"""

VERILOG_WRITE_OUTPUT = """

  always @(*)
    case (state_write)
      `sWriteIdle:
        begin
          awready_wire = 1'b1;
          wready_wire  = 1'b1;
          bvalid_wire  = 1'b0;
        end
      `sWriteWaitData:
        begin
          awready_wire = 1'b0;
          wready_wire  = 1'b1;
          bvalid_wire  = 1'b0;
        end
      `sWriteWaitAddr:
        begin
          awready_wire = 1'b1;
          wready_wire  = 1'b0;
          bvalid_wire  = 1'b0;
        end
      `sWriteResp:
        begin
          awready_wire = 1'b0;
          wready_wire  = 1'b0;
          bvalid_wire  = 1'b1;
        end
      default:
        begin
          awready_wire = 1'b0;
          wready_wire  = 1'b0;
          bvalid_wire  = 1'b0;
        end
    endcase

  assign S_AXI_AWREADY = awready_wire;
  assign S_AXI_WREADY  = wready_wire;
  assign S_AXI_BRESP   = 2'b00;
  assign S_AXI_BVALID  = bvalid_wire;
"""

VERILOG_BEGIN_ARCH = """
"""

VERILOG_END_ARCH = """
endmodule
"""
