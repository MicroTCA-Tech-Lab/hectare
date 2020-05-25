
-- Copyright (c) 2020 Deutsches Elektronen-Synchrotron DESY

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library uvvm_util;
context uvvm_util.uvvm_util_context;

library uvvm_vvc_framework;
use uvvm_vvc_framework.ti_vvc_framework_support_pkg.all;

library bitvis_vip_clock_generator;
context bitvis_vip_clock_generator.vvc_context;

library bitvis_vip_axilite;
context bitvis_vip_axilite.vvc_context;


entity mymodule_tb is
end entity;

architecture sim of mymodule_tb is
begin

  inst_test_harness : entity work.mymodule_th;

  proc_main: process
    variable v_idx : integer;
    variable v_lite_result : bitvis_vip_axilite.vvc_cmd_pkg.t_vvc_result;
  begin

    await_uvvm_initialization(VOID);

    start_clock(CLOCK_GENERATOR_VVCT, 1, "Start clock generator");
    wait for 100 ns;

    axilite_write(AXILITE_VVCT, 1, x"10", x"0000010", "set coef a");
    axilite_write(AXILITE_VVCT, 1, x"14", x"000000f", "set coef b");

    wait for 100 ns;

    axilite_read(AXILITE_VVCT, 1, x"18", "read sum and diff");
    v_idx := get_last_received_cmd_idx(AXILITE_VVCT, 1);
    await_completion(AXILITE_VVCT, 1, 100 ns, "wait for read to complete");
    fetch_result(AXILITE_VVCT, 1, v_idx, v_lite_result);
    log(ID_LOG_HDR, "result = " & to_hstring(v_lite_result(31 downto 0)));

    check_value(v_lite_result(15 downto  0), x"001F", ERROR, "sum  (a + b)");
    check_value(v_lite_result(31 downto 16), x"0001", ERROR, "diff (a - b)");

    wait for 100 ns;
    report_alert_counters(FINAL);
    log(ID_LOG_HDR, "SIMULATION COMPLETED", C_SCOPE);

    std.env.finish;
  end process;
end architecture;
