#!/bin/bash

echo "Environment for scrapper"
echo $DCOS_URL
echo $PORT0

echo "Running metrics process"
python find_marathon_stats.py
