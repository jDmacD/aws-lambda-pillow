#http://stackoverflow.com/questions/4720735/fastest-way-to-download-3-million-objects-from-a-s3-bucket
#https://boto3.readthedocs.org/en/latest/reference/services/s3.html#S3.Client.generate_presigned_url
#https://boto3.readthedocs.org/en/latest/reference/services/cloudfront.html#CloudFront.Client.generate_presigned_url

import os
import sys
import hashlib
import mimetypes
# add webp to mime library, as it is a draft format
mimetypes.add_type('image/webp', '.webp', strict=False)

from eventlet import *
patcher.monkey_patch(all=True)

import boto3
import botocore

import requests
import urllib

import base64
from io import BytesIO

from PIL import Image
from PIL import ImageOps

import cairosvg
import cairocffi as cairo
import rsvg

import time
import itertools
import simplejson as json


s3 = boto3.resource('s3')
s3Client = boto3.client('s3')
pool = GreenPool()
pool.waitall()

def svg_converter(event, context):
	#res = requests.get('https://s3-eu-west-1.amazonaws.com/components.jdmacd/watermark/logo.svg')
	#print res.content
	png = cairosvg.svg2png(url='https://s3-eu-west-1.amazonaws.com/components.jdmacd/watermark/logo.svg')
	return event