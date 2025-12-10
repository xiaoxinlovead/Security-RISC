#!/bin/bash
rm key_leak.log
export LD_LIBRARY_PATH=$PWD/mbedtls/library:$LD_LIBRARY_PATH

for i in $(seq 1 3); do
    echo "Running decrypt: $i / 100"
    ./decrypt
done

echo "All done."

cat key_leak.log
