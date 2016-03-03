#!/bin/bash

set -ex
set -o pipefail

echo "do update"
yum update -y

echo "do dependcy install"
yum install -y \
	gcc \
	#cairo-devel \
	#mock --enablerepo=epel \
	#libffi-devel \
	libtiff-devel \
	libzip-devel \
	libjpeg-devel \
	freetype-devel \
	lcms2-devel \
	libwebp-devel \
	tcl-devel \
	tk-devel

#useradd -s /sbin/nologin mockbuild
#wget https://kojipkgs.fedoraproject.org//packages/librsvg2/2.40.13/2.fc24/src/librsvg2-2.40.13-2.fc24.src.rpm
#rpm -Uhv librsvg2-2.40.13-2.fc24.src.rpm


echo "copy webp packages"
cd /usr/lib64/ 
find . -name "*webp*" | cpio -pdm ~/env/lib64/python2.7/site-packages/
cd ~/

echo "make env"
/usr/bin/virtualenv \
	--python /usr/bin/python env \
	--always-copy


echo "activate env in `pwd`"
source env/bin/activate

echo "install pips"
pip install --upgrade pip
pip install --verbose --use-wheel pillow
pip install --verbose --use-wheel simplejson
pip install --verbose --use-wheel eventlet
pip install --verbose --use-wheel requests
#pip install --verbose --use-wheel cairosvg
#pip install --verbose --use-wheel boto3
deactivate

echo "zip lib and lib64"
cd ~/env/lib/python2.7/site-packages
zip -r9 ~/env.zip *
cd ~/env/lib64/python2.7/site-packages
zip -r9 ~/env.zip *
cd ~/

echo "copy env to s3"
aws s3 cp env.zip s3://code.jdmacd/env.zip --region eu-west-1 --content-type application/zip
echo "copy log to s3"
aws s3 cp /var/log/cloud-init-output.log s3://code.jdmacd/ec2.log --region eu-west-1 --content-type text/plain