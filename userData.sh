#!/bin/bash

yum update -y
yum install -y \
	gcc \
	libtiff-devel \
	libzip-devel \
	libjpeg-devel \
	freetype-devel \
	lcms2-devel \
	libwebp-devel \
	tcl-devel \
	tk-devel

virtualenv env --always-copy
cd /usr/lib64/ 
find . -name "*webp*" | cpio -pdm ~/env/lib64/python2.7/site-packages/
cd ~/
source env/bin/activate
pip install --upgrade pip
pip install --use-wheel pillow
pip install --use-wheel simplejson
pip install --use-wheel eventlet
deactivate

cd ~/env/lib/python2.7/site-packages
zip -r9 ~/env.zip *
cd ~/env/lib64/python2.7/site-packages
zip -r9 ~/env.zip *
cd ~/

aws s3 cp env.zip s3://code.jdmacd/env.zip --region eu-west-1