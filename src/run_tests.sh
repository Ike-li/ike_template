#!/bin/bash
clear
pybabel compile -d i18n/translations

# 避免由于 docs 目录不存在造成的错误
mkdir -p /opt/docs

if [ $STAGE = "development" ]; then
    echo "Run develop tests"
    pytest -x -v -s unittests
else
    echo "Run all tests"
    pytest --run-slow -s
fi
