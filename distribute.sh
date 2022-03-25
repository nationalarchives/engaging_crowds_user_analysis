#!/bin/bash

./galleries/gen_hms_gallery.sh
./galleries/gen_sb_gallery.sh
./galleries/gen_rbge_gallery.sh
./distribute.py
