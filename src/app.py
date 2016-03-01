#http://stackoverflow.com/questions/4720735/fastest-way-to-download-3-million-objects-from-a-s3-bucket
#https://boto3.readthedocs.org/en/latest/reference/services/s3.html#S3.Client.generate_presigned_url
#https://boto3.readthedocs.org/en/latest/reference/services/cloudfront.html#CloudFront.Client.generate_presigned_url

import os
import sys

import mimetypes
mimetypes.add_type('image/webp', '.webp', strict=False)
mimetypes.add_type('image/jpeg', '.jpg', strict=False)
mimetypes.add_type('image/jpeg', '.jpeg', strict=False)
mimetypes.init()

from eventlet import *
patcher.monkey_patch(all=True)

import boto3
import botocore

import base64
from io import BytesIO
from io import StringIO

from PIL import Image
from PIL import ImageOps

import time
import itertools
import json


s3 = boto3.resource('s3')
s3Client = boto3.client('s3')
pool = GreenPool()
pool.waitall()

def clean_extension(extension):

	if extension.lower() == 'jpg' or  extension.lower() == 'jpeg':
		return 'jpeg'
	elif extension.lower() == 'tiff' or extension.lower() == 'tif':
		return 'tiff'
	elif extension.lower() == 'webp':
		return 'webp'
	elif extension.lower() == 'png':
		return 'png'
	elif extension.lower() == 'bmp':
		return 'bmp'
	else:
		return extension

def composite_layers(layers):
	base_img = None

	for layer in pool.imap(get_image, layers):

		img = layer['img']
		offset = (layer['x'], layer['y'])

		if base_img == None:
			base_img = Image.new('RGB', img.size)

		if img.mode == 'RGBA':
			base_img.paste(img, offset, img)
		else:	
			base_img.paste(img, offset)

	return base_img

def data_url(img, quality, format, Type):

	start_time = time.time()

	image_buffer = BytesIO()
	img.save(image_buffer, quality=quality, format=format)
	imgStr = base64.b64encode(image_buffer.getvalue())
	dataUrl = 'data:' + Type +';base64,' + imgStr.decode('utf-8')

	print('dataUrl conversion in ' + str(time.time() - start_time))

	return dataUrl

def S3_url(Key):

	return s3Client.generate_presigned_url('get_object', Params = {'Bucket': 'components.jdmacd', 'Key': Key}, ExpiresIn = 3600)

def get_image(layer):

	key = layer['key']

	start_time = time.time()

	object = s3.Object('components.jdmacd', key)

	try:
		res = object.get()
	except:
		print('get fail: ' + key)
	
	print('get success: ' + key + ' in ' + str(time.time() - start_time))

	layer['img'] = Image.open(res['Body'])

	return layer

def save_image(img, quality, format, Type, Key):

	object = s3.Object('components.jdmacd', Key)
	image_buffer = BytesIO()
	img.save(image_buffer, quality=quality, format=format)
	res = object.put(Body=image_buffer.getvalue(), ContentType=Type)
	return res


def composite_handler(event, context):

	quality = event['quality']
	extension = clean_extension(event['extension'])
	Key =  event['_id'] + '.' + extension
	MimeType = mimetypes.guess_type(Key, strict=False)[0]

	composite_image = composite_layers(event['layers'])

	if event['dataUrl']:
		print('returning as dataUrl')
		return data_url(composite_image, quality=quality, format=extension, Type=MimeType)
	else:
		save_image(composite_image, quality=quality, format=extension, Type=MimeType, Key=Key)
		return S3_url(Key)


