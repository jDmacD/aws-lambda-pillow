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

import base64
from io import BytesIO
from io import StringIO

from PIL import Image
from PIL import ImageOps

import time
import itertools
import simplejson as json


s3 = boto3.resource('s3')
s3Client = boto3.client('s3')
pool = GreenPool()
pool.waitall()

default_bucket = 'components.jdmacd'

def clean_format(format):

	if format.lower() == 'jpg' or  format.lower() == 'jpeg':
		return 'jpeg'
	elif format.lower() == 'tiff' or format.lower() == 'tif':
		return 'tiff'
	elif format.lower() == 'webp':
		return 'webp'
	elif format.lower() == 'png':
		return 'png'
	elif format.lower() == 'bmp':
		return 'bmp'
	else:
		return format

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

def S3_url(Key, Bucket):

	return s3Client.generate_presigned_url('get_object', Params = {'Bucket': Bucket, 'Key': Key}, ExpiresIn = 3600)

def get_image(layer):

	key = layer['key']

	try:
		bucket = layer['bucket']
	except:
		bucket = default_bucket

	start_time = time.time()

	object = s3.Object(bucket, key)

	try:
		res = object.get()
	except:
		print('get fail: ' + key)
	
	print('get success: ' + key + ' in ' + str(time.time() - start_time))

	layer['img'] = Image.open(res['Body'])

	return layer

def save_image(img, quality, format, Type, Key, Bucket):

	object = s3.Object(Bucket, Key)
	image_buffer = BytesIO()
	img.save(image_buffer, quality=quality, format=format)
	res = object.put(Body=image_buffer.getvalue(), ContentType=Type)
	return res


def composite_handler(event, context):

	quality = event['quality']
	mode = event['mode']
	format = clean_format(event['format'])

	try:
		Bucket = event['bucket']
	except:
		Bucket = default_bucket

	try:
		Key =  event['name'] + '.' + format
	except:
		Key = hashlib.md5(json.dumps(event)).hexdigest() + '.' + format

	MimeType = mimetypes.guess_type(Key, strict=False)[0]

	print(quality, mode, format, Bucket, Key, MimeType)

	if mode == 'data':

		composite_image = composite_layers(event['layers'])

		return data_url(composite_image, quality=quality, format=format, Type=MimeType)

	elif mode == 's3':

		try:
			s3Client.head_object(Bucket=Bucket, Key=Key)
			return S3_url(Key=Key, Bucket=Bucket)
		except:
			composite_image = composite_layers(event['layers'])
			save_image(composite_image, quality=quality, format=format, Type=MimeType, Key=Key ,Bucket=Bucket)
			return S3_url(Key=Key, Bucket=Bucket)


