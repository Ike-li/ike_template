#!/bin/bash

cd /Users/ikeli/project/blackjack_flask

echo "使用 yapf 格式化代码..."
yapf -ir src

echo "使用 isort 格式化代码..."
isort -rc src
