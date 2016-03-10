#!/bin/bash

export PKG_CONFIG_PATH=/usr/lib/pkgconfig:/usr/lib64/pkgconfig:/usr/share/pkgconfig
export LD_LIBRARY_PATH=/usr/lib

sudo yum update -y
sudo yum install -y gcc

sudo yum-config-manager --add-repo https://raw.githubusercontent.com/jDmacD/cuddly-octo-meme/master/fedora.repo
sudo yum-config-manager --enable fedora

yum repolist all

sudo yum install -y --disableplugin=priorities \
flex \
bison \
zlib-devel \
libffi-devel \
gettext \
pcre-devel \
cairo-devel \
pango-devel \
libtiff-devel \
libjpeg-devel \
libpng-devel \
pygobject2


#GLIB
wget -N http://ftp.gnome.org/pub/gnome/sources/glib/2.46/glib-2.46.2.tar.xz

tar -xf glib-2.46.2.tar.xz
cd glib-2.46.2

./configure --prefix=/usr && make
sudo make install

pkg-config --modversion glib-2.0

cd ~/


#GI
wget -N http://ftp.gnome.org/pub/gnome/sources/gobject-introspection/1.46/gobject-introspection-1.46.0.tar.xz
tar -xf gobject-introspection-1.46.0.tar.xz
cd gobject-introspection-1.46.0

./configure --prefix=/usr --disable-static
sudo make install

cd ~/

#ATK
wget http://ftp.gnome.org/pub/gnome/sources/atk/2.18/atk-2.18.0.tar.xz
tar -xf atk-2.18.0.tar.xz
cd atk-2.18.0

./configure --prefix=/usr && make
sudo make install

cd ~/

#PIXBUF
wget http://ftp.gnome.org/pub/gnome/sources/gdk-pixbuf/2.32/gdk-pixbuf-2.32.3.tar.xz
tar -xf gdk-pixbuf-2.32.3.tar.xz
cd gdk-pixbuf-2.32.3

./configure --prefix=/usr && make
sudo make install

pkg-config --modversion gdk-pixbuf-2.0

cd ~/

#GTK
wget http://ftp.gnome.org/pub/gnome/sources/gtk+/2.24/gtk+-2.24.30.tar.xz
tar -xf gtk+-2.24.30.tar.xz
cd gtk+-2.24.30

./configure --prefix=/usr && make
sudo make install





