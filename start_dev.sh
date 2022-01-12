#!/bin/bash

test -d env && source env/bin/activate

cd src
pre-commit install

# 如果需要删除 pre-commit 检查，可以使用:
# pre-commit uninstall
