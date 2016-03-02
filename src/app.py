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

	if format.lower()  in ['jpg', 'jpeg']:
		return 'jpeg'
	elif format.lower() in ['tiff', 'tif']:
		return 'tiff'
	elif format.lower() in ['webp']:
		return 'webp'
	elif format.lower() in ['png']:
		return 'png'
	elif format.lower() == ['bmp']:
		return 'bmp'
	else:
		return format

def to_pixels(part, whole):

	part_type = type(part)
	if part_type is float or part_type is int:
		#part is in pixels
		return part
	elif part_type is unicode:
		#part is in percentage, convert to pixels
		pixels = float(whole) /100 * float(part)
		return pixels

def unknown_side(known, side_1, side_2):

	return float(known) * float(side_1) / float(side_2)

def composite_images(images):

	base_img = None

	for image in pool.imap(get_image, images):

		image = resize_image(image)

		img = image['img']

		if type(image['x']) is float or type(image['x']) is int:
			x = int(image['x'])

		if type(image['y']) is float or type(image['y']) is int:
			y = int(image['y'])

		if base_img == None:
			base_img = Image.new('RGB', img.size)

		if img.mode == 'RGBA':
			base_img.paste(img, (x,y), img)
		else:	
			base_img.paste(img, (x,y))

	return base_img

def resize_image(image):

	try:
		height = image['height']
	except:
		height = None

	try:
		width = image['width']
	except:
		width = None

	i_width, i_height = image['img'].size

	if height == None and width == None:
		# No height or width supplied
		print('no height or width')
	else:
		if height != None:
			height = to_pixels(part=height, whole=i_height)
		else:
			# Calculate height from width
			height = unknown_side(known=to_pixels(width, i_width), side_1=i_height, side_2=i_width)
		
		if width != None:
			width = to_pixels(part=width, whole=i_width)
		else:
			# Calulate width from height
			width = unknown_side(known=to_pixels(height, i_height), side_1=i_width, side_2=i_height)


	image['img'] = image['img'].resize((int(width),int(height)), Image.ANTIALIAS)

	return image

def data_url(img, quality, format, ContentType):

	start_time = time.time()

	img_buffer = BytesIO()
	img.save(img_buffer, quality=quality, format=format)
	imgStr = base64.b64encode(img_buffer.getvalue())
	dataUrl = 'data:' + ContentType +';base64,' + imgStr.decode('utf-8')

	print('dataUrl conversion in ' + str(time.time() - start_time))

	return dataUrl

def S3_url(Key, Bucket):

	return s3Client.generate_presigned_url('get_object', Params = {'Bucket': Bucket, 'Key': Key}, ExpiresIn = 3600)

def get_image(image):

	key = image['key']

	try:
		bucket = image['bucket']
	except:
		bucket = bucket_in

	start_time = time.time()

	object = s3.Object(bucket, key)

	try:
		res = object.get()
	except:
		print('get fail: ' + key)
	
	print('get success: ' + key + ' in ' + str(time.time() - start_time))

	image['img'] = Image.open(res['Body'])

	return image

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

		composite_image = composite_images(event['images'])

		return data_url(composite_image, quality=quality, format=format, ContentType=ContentType)

	elif mode == 's3':

		try:
			s3Client.head_object(Bucket=Bucket, Key=Key)
			return S3_url(Key=Key, Bucket=Bucket)
		except:
			composite_image = composite_images(event['images'])
			save_image(composite_image, quality=quality, format=format, ContentType=ContentType, Key=Key ,Bucket=Bucket)
			return S3_url(Key=Key, Bucket=Bucket)


