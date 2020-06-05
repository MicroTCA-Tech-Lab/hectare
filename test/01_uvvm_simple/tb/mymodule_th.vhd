
-- Copyright (c) 2020 Deutsches Elektronen-Synchrotron DESY
--
-- See LICENSE.txt for license details.

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library uvvm_vvc_framework;
use uvvm_vvc_framework.ti_vvc_framework_support_pkg.all;

library bitvis_vip_clock_generator;

library bitvis_vip_axilite;
use bitvis_vip_axilite.axilite_bfm_pkg.t_axilite_bfm_config;
use bitvis_vip_axilite.axilite_bfm_pkg.C_AXILITE_BFM_CONFIG_DEFAULT;

use work.mymodule_pkg.ColorsEnum_t;

entity mymodule_th is
end entity;

architecture arch of mymodule_th is
  constant C_CLK_PERIOD : time    := 10 ns;
  constant G_ADDR_W : integer := 8;
  constant C_AXI4LITE_CONFIG : t_axilite_bfm_config := C_AXILITE_BFM_CONFIG_DEFAULT;

  signal status_color_sel_rbv_i : ColorsEnum_t;
  signal status_ready_o : std_logic;
  signal status_ready_i : std_logic;
  signal control_color_sel_o : ColorsEnum_t;
  signal control_color_sel_swmod : std_logic;
  signal control_enable_o : std_logic;
  signal coef_a_a_o    : std_logic_vector(15 downto 0);
  signal coef_b_b_o    : std_logic_vector(15 downto 0);
  signal result_sum_o  : std_logic_vector(15 downto 0);
  signal result_sum_i  : std_logic_vector(15 downto 0);
  signal result_diff_o : std_logic_vector(15 downto 0);
  signal result_diff_i : std_logic_vector(15 downto 0);
  signal clk           : std_logic;
  signal reset         : std_logic;
  signal S_AXI_AWADDR  : std_logic_vector(G_ADDR_W-1 downto 0);
  signal S_AXI_AWPROT  : std_logic_vector(2 downto 0);
  signal S_AXI_AWVALID : std_logic;
  signal S_AXI_AWREADY : std_logic;
  signal S_AXI_WDATA   : std_logic_vector(32-1 downto 0);
  signal S_AXI_WSTRB   : std_logic_vector(32/8-1 downto 0);
  signal S_AXI_WVALID  : std_logic;
  signal S_AXI_WREADY  : std_logic;
  signal S_AXI_BRESP   : std_logic_vector(1 downto 0);
  signal S_AXI_BVALID  : std_logic;
  signal S_AXI_BREADY  : std_logic;
  signal S_AXI_ARADDR  : std_logic_vector(G_ADDR_W-1 downto 0);
  signal S_AXI_ARPROT  : std_logic_vector(2 downto 0);
  signal S_AXI_ARVALID : std_logic;
  signal S_AXI_ARREADY : std_logic;
  signal S_AXI_RDATA   : std_logic_vector(32-1 downto 0);
  signal S_AXI_RRESP   : std_logic_vector(1 downto 0);
  signal S_AXI_RVALID  : std_logic;
  signal S_AXI_RREADY  : std_logic;

  type color_pipeline_t is array(natural range<>) of ColorsEnum_t;
  signal color_pipeline : color_pipeline_t(0 to 2) := (others => RED);

begin

  inst_ti_uvvm_engine : entity uvvm_vvc_framework.ti_uvvm_engine;

  inst_clock_generator_vvc : entity bitvis_vip_clock_generator.clock_generator_vvc
  generic map (
    GC_INSTANCE_IDX    => 1,
    GC_CLOCK_NAME      => "Clock",
    GC_CLOCK_PERIOD    => C_CLK_PERIOD,
    GC_CLOCK_HIGH_TIME => C_CLK_PERIOD / 2
  )
  port map (
    clk => clk
  );

  proc_reset: process
  begin
    reset <= '1';
    for i in 0 to 5 loop
      wait until rising_edge(clk);
    end loop;
    reset <= '0';
    wait;
  end process;

  inst_axi_lite_master : entity bitvis_vip_axilite.axilite_vvc
  generic map (
    GC_ADDR_WIDTH  => G_ADDR_W,
    GC_DATA_WIDTH => 32,
    GC_INSTANCE_IDX => 1,
    GC_AXILITE_CONFIG => C_AXI4LITE_CONFIG
  )
  port map (
    clk                                                 => clk,
    axilite_vvc_master_if.write_address_channel.awaddr  => S_AXI_AWADDR,
    axilite_vvc_master_if.write_address_channel.awvalid => S_AXI_AWVALID,
    axilite_vvc_master_if.write_address_channel.awprot  => S_AXI_AWPROT,
    axilite_vvc_master_if.write_address_channel.awready => S_AXI_AWREADY,
    axilite_vvc_master_if.write_data_channel.wdata      => S_AXI_WDATA,
    axilite_vvc_master_if.write_data_channel.wstrb      => S_AXI_WSTRB,
    axilite_vvc_master_if.write_data_channel.wvalid     => S_AXI_WVALID,
    axilite_vvc_master_if.write_data_channel.wready     => S_AXI_WREADY,
    axilite_vvc_master_if.write_response_channel.bready => S_AXI_BREADY,
    axilite_vvc_master_if.write_response_channel.bresp  => S_AXI_BRESP,
    axilite_vvc_master_if.write_response_channel.bvalid => S_AXI_BVALID,
    axilite_vvc_master_if.read_address_channel.araddr   => S_AXI_ARADDR,
    axilite_vvc_master_if.read_address_channel.arvalid  => S_AXI_ARVALID,
    axilite_vvc_master_if.read_address_channel.arprot   => S_AXI_ARPROT,
    axilite_vvc_master_if.read_address_channel.arready  => S_AXI_ARREADY,
    axilite_vvc_master_if.read_data_channel.rready      => S_AXI_RREADY,
    axilite_vvc_master_if.read_data_channel.rdata       => S_AXI_RDATA,
    axilite_vvc_master_if.read_data_channel.rresp       => S_AXI_RRESP,
    axilite_vvc_master_if.read_data_channel.rvalid      => S_AXI_RVALID
  );

  inst_dut: entity work.mymodule
  generic map (
    G_ADDR_W => G_ADDR_W
  )
  port map (
    status_color_sel_rbv_i => status_color_sel_rbv_i,
    status_ready_o => status_ready_o,
    status_ready_i => status_ready_i,
    control_color_sel_o => control_color_sel_o,
    control_color_sel_swmod => control_color_sel_swmod,
    control_enable_o => control_enable_o,
    coef_a_a_o => coef_a_a_o,
    coef_b_b_o => coef_b_b_o,
    result_sum_o => result_sum_o,
    result_sum_i => result_sum_i,
    result_diff_o => result_diff_o,
    result_diff_i => result_diff_i,
    clk              => clk             ,
    reset            => reset           ,
    S_AXI_AWADDR     => S_AXI_AWADDR    ,
    S_AXI_AWPROT     => S_AXI_AWPROT    ,
    S_AXI_AWVALID    => S_AXI_AWVALID   ,
    S_AXI_AWREADY    => S_AXI_AWREADY   ,
    S_AXI_WDATA      => S_AXI_WDATA     ,
    S_AXI_WSTRB      => S_AXI_WSTRB     ,
    S_AXI_WVALID     => S_AXI_WVALID    ,
    S_AXI_WREADY     => S_AXI_WREADY    ,
    S_AXI_BRESP      => S_AXI_BRESP     ,
    S_AXI_BVALID     => S_AXI_BVALID    ,
    S_AXI_BREADY     => S_AXI_BREADY    ,
    S_AXI_ARADDR     => S_AXI_ARADDR    ,
    S_AXI_ARPROT     => S_AXI_ARPROT    ,
    S_AXI_ARVALID    => S_AXI_ARVALID   ,
    S_AXI_ARREADY    => S_AXI_ARREADY   ,
    S_AXI_RDATA      => S_AXI_RDATA     ,
    S_AXI_RRESP      => S_AXI_RRESP     ,
    S_AXI_RVALID     => S_AXI_RVALID    ,
    S_AXI_RREADY     => S_AXI_RREADY
  );

  -- simple logic
  result_sum_i  <= std_logic_vector(unsigned(coef_a_a_o) + unsigned(coef_b_b_o));
  result_diff_i <= std_logic_vector(unsigned(coef_a_a_o) - unsigned(coef_b_b_o));

  proc_color_pipeline: process (clk)
  begin
    if rising_edge(clk) then
      if control_color_sel_swmod = '1' then
        color_pipeline(0) <= control_color_sel_o;
        for i in 1 to color_pipeline'length-1 loop
          color_pipeline(i) <= color_pipeline(i-1);
        end loop;
      end if;
    end if;
  end process;

  status_color_sel_rbv_i <= color_pipeline(color_pipeline'high);
end architecture;
