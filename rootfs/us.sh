#!/bin/bash
test="$(cat test*)"
test=($test)
echo ${test[0]}
