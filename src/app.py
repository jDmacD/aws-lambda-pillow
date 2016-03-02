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

from PIL import Image
from PIL import ImageOps

import time
import itertools
import simplejson as json


s3 = boto3.resource('s3')
s3Client = boto3.client('s3')
pool = GreenPool()
pool.waitall()

with open('config.json') as data_file:    
    config = json.load(data_file)

bucket_in = config['bucket_in']
bucket_out = config['bucket_out']

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

		layer = resize_layer(layer)

		img = layer['img']

		if type(layer['x']) is float or type(layer['x']) is int:
			x = int(layer['x'])

		if type(layer['y']) is float or type(layer['y']) is int:
			y = int(layer['y'])

		if base_img == None:
			base_img = Image.new('RGB', img.size)

		if img.mode == 'RGBA':
			base_img.paste(img, (x,y), img)
		else:	
			base_img.paste(img, (x,y))

	return base_img

def resize_layer(layer):

	try:
		h_type = type(layer['height'])
		if h_type is float or h_type is int:
			height = int(layer['height'])
			
		elif h_type is unicode:
			# height as a percentage
			height = int((layer['img'].size[1] / 100) * int(layer['height']))
			print(height)
	except:

	try:
		w_type = type(layer['width'])
		if w_type is float or w_type is int:
			width = int(layer['width'])

		elif w_type is unicode:
			# width as a percentage
			width = int((layer['img'].size[0] / 100) * int(layer['width']))
			print(width)
	except:

	layer['img'] = layer['img'].resize((width,height), Image.ANTIALIAS)

	return layer

def data_url(img, quality, format, ContentType):

	start_time = time.time()

	image_buffer = BytesIO()
	img.save(image_buffer, quality=quality, format=format)
	imgStr = base64.b64encode(image_buffer.getvalue())
	dataUrl = 'data:' + ContentType +';base64,' + imgStr.decode('utf-8')

	print('dataUrl conversion in ' + str(time.time() - start_time))

	return dataUrl

def S3_url(Key, Bucket):

	return s3Client.generate_presigned_url('get_object', Params = {'Bucket': Bucket, 'Key': Key}, ExpiresIn = 3600)

def get_image(layer):

	key = layer['key']

	try:
		bucket = layer['bucket']
	except:
		bucket = bucket_in

	start_time = time.time()

	object = s3.Object(bucket, key)

	try:
		res = object.get()
	except:
		print('get fail: ' + key)
	
	print('get success: ' + key + ' in ' + str(time.time() - start_time))

	layer['img'] = Image.open(res['Body'])

	return layer

def save_image(img, quality, format, ContentType, Key, Bucket):

	object = s3.Object(Bucket, Key)
	image_buffer = BytesIO()
	img.save(image_buffer, quality=quality, format=format)
	res = object.put(Body=image_buffer.getvalue(), ContentType=ContentType)
	return res


def composite_handler(event, context):

	quality = event['quality']
	mode = event['mode']
	format = clean_format(event['format'])

	try:
		Bucket = event['bucket']
	except:
		Bucket = bucket_out

	try:
		Key =  event['name'] + '.' + format
	except:
		Key = hashlib.md5(json.dumps(event)).hexdigest() + '.' + format

	ContentType = mimetypes.guess_type(Key, strict=False)[0]

	if mode == 'data':

		composite_image = composite_layers(event['layers'])

		return data_url(composite_image, quality=quality, format=format, ContentType=ContentType)

	elif mode == 's3':

		try:
			s3Client.head_object(Bucket=Bucket, Key=Key)
			return S3_url(Key=Key, Bucket=Bucket)
		except:
			composite_image = composite_layers(event['layers'])
			save_image(composite_image, quality=quality, format=format, ContentType=ContentType, Key=Key ,Bucket=Bucket)
			return S3_url(Key=Key, Bucket=Bucket)


