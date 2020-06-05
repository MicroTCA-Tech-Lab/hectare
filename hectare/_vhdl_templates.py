"""
Copyright (c) 2020 Deutsches Elektronen-Synchrotron DESY.

See LICENSE.txt for license details.
"""

VHDL_LIBS = """
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
"""

VHDL_PORTS_AXI = """
    clk           : in std_logic;
    reset         : in std_logic;
    S_AXI_AWADDR  : in std_logic_vector(G_ADDR_W-1 downto 0);
    S_AXI_AWPROT  : in std_logic_vector(2 downto 0);
    S_AXI_AWVALID : in std_logic;
    S_AXI_AWREADY : out std_logic;
    S_AXI_WDATA   : in std_logic_vector(32-1 downto 0);
    S_AXI_WSTRB   : in std_logic_vector(32/8-1 downto 0);
    S_AXI_WVALID  : in std_logic;
    S_AXI_WREADY  : out std_logic;
    S_AXI_BRESP   : out std_logic_vector(1 downto 0);
    S_AXI_BVALID  : out std_logic;
    S_AXI_BREADY  : in std_logic;
    S_AXI_ARADDR  : in std_logic_vector(G_ADDR_W-1 downto 0);
    S_AXI_ARPROT  : in std_logic_vector(2 downto 0);
    S_AXI_ARVALID : in std_logic;
    S_AXI_ARREADY : out std_logic;
    S_AXI_RDATA   : out std_logic_vector(32-1 downto 0);
    S_AXI_RRESP   : out std_logic_vector(1 downto 0);
    S_AXI_RVALID  : out std_logic;
    S_AXI_RREADY  : in std_logic
"""

VHDL_INTERNAL_SIG_DEFS = """
  -- read
  type t_state_read is (sReadIdle, sReadValid);
  signal state_read : t_state_read;
  
  signal rdata_reg : std_logic_vector(31 downto 0);
  signal raddr_word : integer;
  
  signal arready_wire : std_logic;
  signal rvalid_wire : std_logic;
  
  -- write
  type t_state_write is (sWriteIdle, sWriteWaitData, sWriteWaitAddr, sWriteResp);
  signal state_write : t_state_write;
  signal state_write_prev : t_state_write;
  
  signal waddr_reg : std_logic_vector(G_ADDR_W-1 downto 0);
  signal wdata_reg : std_logic_vector(31 downto 0);
  
  signal waddr_word : integer;
  
  signal awready_wire : std_logic;
  signal wready_wire : std_logic;
  signal bvalid_wire : std_logic;
"""

VHDL_FSM_READ = """
  proc_state_read: process (clk)
  begin
    if rising_edge(clk) then
      if reset = '1' then
        state_read <= sReadIdle;
      else
        case state_read is
          when sReadIdle =>
            if S_AXI_ARVALID = '1' then
              state_read <= sReadValid;
            end if;
          when sReadValid =>
            if S_AXI_RREADY = '1' then
              state_read <= sReadIdle;
            end if;
        end case;
      end if;
    end if;
  end process;

  raddr_word <= to_integer(unsigned(S_AXI_ARADDR(G_ADDR_W-1 downto 2)));
"""

VHDL_FSM_WRITE = """
  proc_read_output: process (state_read)
  begin
    case state_read is
      when sReadIdle =>
        arready_wire <= '1';
        rvalid_wire <= '0';
      when sReadValid =>
        arready_wire <= '0';
        rvalid_wire <= '1';
      when others =>
        arready_wire <= '0';
        rvalid_wire <= '0';
    end case;
  end process;

  S_AXI_ARREADY <= arready_wire;
  S_AXI_RVALID <= rvalid_wire;
  S_AXI_RDATA <= rdata_reg;
  S_AXI_RRESP <= "00";

  proc_state_write_prev: process (clk) begin
    if rising_edge(clk) then
      state_write_prev <= state_write;
    end if;
  end process;

  proc_state_write: process (clk) begin
    if rising_edge (clk) then
      if reset = '1' then
        state_write <= sWriteIdle;
      else
        case state_write is
          when sWriteIdle =>
            if S_AXI_AWVALID = '1' and S_AXI_WVALID = '1' then
              state_write <= sWriteResp;
              waddr_reg <= S_AXI_AWADDR;
              wdata_reg <= S_AXI_WDATA;
            elsif S_AXI_AWVALID = '1' and S_AXI_WVALID = '0' then
              state_write <= sWriteWaitData;
              waddr_reg <= S_AXI_AWADDR;
            elsif S_AXI_AWVALID = '0' and S_AXI_WVALID = '1' then
              state_write <= sWriteWaitAddr;
              wdata_reg <= S_AXI_WDATA;
            end if;
          when sWriteWaitData =>
            if S_AXI_WVALID = '1' then
              state_write <= sWriteResp;
              wdata_reg <= S_AXI_WDATA;
            end if;
          when sWriteWaitAddr =>
            if S_AXI_AWVALID = '1' then
              state_write <= sWriteResp;
              waddr_reg <= S_AXI_AWADDR;
            end if;
          when sWriteResp =>
            if S_AXI_BREADY = '1' then
              state_write <= sWriteIdle;
            end if;
        end case;
      end if;
    end if;
  end process;

  waddr_word <= to_integer(unsigned(waddr_reg(G_ADDR_W-1 downto 2)));
"""

VHDL_WRITE_OUTPUT = """

  proc_write_output: process (state_write) begin
    case state_write is
      when sWriteIdle =>
        awready_wire <= '1';
        wready_wire <= '1';
        bvalid_wire <= '0';
      when sWriteWaitData =>
        awready_wire <= '0';
        wready_wire <= '1';
        bvalid_wire <= '0';
      when sWriteWaitAddr =>
        awready_wire <= '1';
        wready_wire <= '0';
        bvalid_wire <= '0';
      when sWriteResp =>
        awready_wire <= '0';
        wready_wire <= '0';
        bvalid_wire <= '1';
      when others =>
        awready_wire <= '0';
        wready_wire <= '0';
        bvalid_wire <= '0';
    end case;
  end process;

  S_AXI_AWREADY <= awready_wire;
  S_AXI_WREADY <= wready_wire;
  S_AXI_BRESP <= "00";
  S_AXI_BVALID <= bvalid_wire;
"""

VHDL_BEGIN_ARCH = """
"""

VHDL_END_ARCH = """
end architecture;
"""
