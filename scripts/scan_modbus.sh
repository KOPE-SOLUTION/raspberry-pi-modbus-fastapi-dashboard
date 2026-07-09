#!/bin/bash

for id in $(seq 1 20); do
    echo "Scan ID $id"
    mbpoll -m rtu -b 9600 -P none -a $id -t 4 -r 1 -c 1 /dev/ttyUSB0 -1 -q && echo "FOUND $id"
done