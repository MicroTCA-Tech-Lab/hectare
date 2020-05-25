"""
Copyright (c) 2020 Deutsches Elektronen-Synchrotron DESY.
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
"""
