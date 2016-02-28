#http://stackoverflow.com/questions/4720735/fastest-way-to-download-3-million-objects-from-a-s3-bucket
#https://boto3.readthedocs.org/en/latest/reference/services/s3.html#S3.Client.generate_presigned_url
#https://boto3.readthedocs.org/en/latest/reference/services/cloudfront.html#CloudFront.Client.generate_presigned_url

import os
import sys

import mimetypes
mimetypes.add_type('image/webp', '.webp')
mimetypes.add_type('image/jpeg', '.jpg')
mimetypes.add_type('image/jpeg', '.jpeg')

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

def data_url(img, quality, format, Type):

	start_time = time.time()

	image_buffer = BytesIO()
	img.save(image_buffer, quality=quality, format=format)
	imgStr = base64.b64encode(image_buffer.getvalue())
	dataUrl = 'data:' + Type +';base64,' + imgStr.decode('utf-8')

	print('dataUrl conversion in ' + str(time.time() - start_time))

	print(sys.getsizeof(dataUrl))

	return dataUrl

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

def composite_handler(event, context):

	base_img = None

	quality = event['quality']
	Key = '_id.' + event['extension']
	Type = mimetypes.guess_type(Key)[0]
	extension = mimetypes.guess_extension(Type)
	Key = event['_id'] + extension

	print(Type, extension, Key)

	for layer in pool.imap(get_image, event['layers']):

		img = layer['img']
		offset = (layer['x'], layer['y'])

		if base_img == None:
			base_img = Image.new('RGB', img.size)

		if img.mode == 'RGBA':
			base_img.paste(img, offset, img)
		else:	
			base_img.paste(img, offset)

	if event['dataUrl']:
		print('returning as dataUrl')
		return data_url(base_img, quality=quality, format=extension, Type=Type)
	else:
		object = s3.Object('components.jdmacd', Key)
		image_buffer = BytesIO()
		base_img.save(image_buffer, quality=quality, format=extension)
		res = object.put(Body=image_buffer.getvalue(), ContentType=Type)
		return s3Client.generate_presigned_url('get_object', Params = {'Bucket': 'components.jdmacd', 'Key': Key}, ExpiresIn = 3600)

