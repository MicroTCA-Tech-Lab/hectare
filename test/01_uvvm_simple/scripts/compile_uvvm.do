
# check if UVVM_PATH is defined in environment
# otherwise assume UVVM is installed in $HOME dir
# this should point to the top directory for UVVM

if {[info exists ::env(UVVM_PATH)]} {
    echo "UVVM_PATH: using environment"
    set UVVM_PATH $env(UVVM_PATH)
} else {
    echo "UVVM_PATH: using default"
    set UVVM_PATH $env(HOME)/FPGA/UVVM/UVVM
}

echo "UVVM_PATH set to $UVVM_PATH"


## compile

# UVVM utils
set lib_name "uvvm_util"
do $UVVM_PATH/$lib_name/script/compile_src.do $UVVM_PATH/$lib_name

# VVC framework
set lib_name "uvvm_vvc_framework"
do $UVVM_PATH/$lib_name/script/compile_src.do $UVVM_PATH/$lib_name

# scoreboard
set lib_name "bitvis_vip_scoreboard"
do $UVVM_PATH/$lib_name/script/compile_src.do $UVVM_PATH/$lib_name

# clock generator
set lib_name "bitvis_vip_clock_generator"
do $UVVM_PATH/$lib_name/script/compile_src.do $UVVM_PATH/$lib_name

# BFM: axi lite
set lib_name "bitvis_vip_axilite"
do $UVVM_PATH/$lib_name/script/compile_src.do $UVVM_PATH/$lib_name

quit

