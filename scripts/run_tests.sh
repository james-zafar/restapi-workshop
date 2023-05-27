#!/bin/bash

set -e

cd "$(dirname "$0")/.." || exit

python -W ignore -m unittest discover -s "$(pwd)/app/test/" -p 'test*'
