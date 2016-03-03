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
	elif format.lower() in ['bmp']:
		return 'bmp'
	elif format.lower() in ['gif']:
		return 'gif'
	else:
		return format.lower()

def to_pixels(part, whole):

	part_type = type(part)
	if part_type is float or part_type is int:
		#part is in pixels
		return part
	elif part_type is unicode:
		#part is a percentage, convert to pixels
		pixels = float(whole) /100 * float(part)
		return pixels

def unknown_side(known, side_1, side_2):

	return float(known) * float(side_1) / float(side_2)

def composite_images(images):

	base_img = None

	for image in pool.imap(get_image, images):

		image = resize_image(image)

		img = image['img']

		if 'r' in image:
			img = img.rotate(int(image['r']), expand=True)

		if base_img == None:
			base_img = Image.new('RGB', img.size)

		if 'x' in image:
			x = to_pixels(image['x'], base_img.size[0])
		elif 'cx' in image:
			x = to_pixels(image['cx'], base_img.size[0]) - (img.size[0]/2)
		else:
			x = 0

		if 'y' in image:
			y = to_pixels(image['y'], base_img.size[1])
		if 'cy' in image:
			y = to_pixels(image['cy'], base_img.size[1]) - (img.size[1]/2)
		else:
			y = 0

		if img.mode == 'RGBA':
			base_img.paste(img, ( int(x) , int(y) ), img)
		else:	
			base_img.paste(img, ( int(x) , int(y) ) )

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

	if height == None and width == None:
		# No height or width supplied, return as is
		return image
	else:

		i_width, i_height = image['img'].size

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

	if 'Key' in image:
		Key = image['Key']

		try:
			bucket = image['bucket']
		except:
			bucket = bucket_in

		object = s3.Object(bucket, Key)

		try:
			res = object.get()
		except:
			print('get fail: ' + Key)
		
		image['img'] = Image.open(res['Body'])

	elif 'url' in image:
		# http://pillow.readthedocs.org/en/3.1.x/releasenotes/2.8.0.html
		image['img'] = Image.open(requests.get(image['url'], stream=True).raw)

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

	try:
		Bucket = event['bucket']
	except:
		Bucket = bucket_out

	try:
		Key =  event['Key']
	except:
		Key = hashlib.md5(json.dumps(event)).hexdigest()

	if '.' in Key:
		format = clean_foemat(Key.split('.')[1])
	else:
		format = clean_format(event['format'])
		Key = Key + '.' + format


	ContentType = mimetypes.guess_type(Key, strict=False)[0]

	if mode == 'DATA':

		composite_image = composite_images(event['images'])
		return data_url(composite_image, quality=quality, format=format, ContentType=ContentType)

	elif mode == 'S3URL':

		try:
			s3Client.head_object(Bucket=Bucket, Key=Key)
			return S3_url(Key=Key, Bucket=Bucket)
		except:
			composite_image = composite_images(event['images'])
			save_image(composite_image, quality=quality, format=format, ContentType=ContentType, Key=Key ,Bucket=Bucket)
			return S3_url(Key=Key, Bucket=Bucket)

	elif mode == 'S3':

		try:
			res = s3Client.head_object(Bucket=Bucket, Key=Key)
			print(res)
			return {'Bucket': Bucket, 'Key':Key}
		except:
			composite_image = composite_images(event['images'])
			res = save_image(composite_image, quality=quality, format=format, ContentType=ContentType, Key=Key ,Bucket=Bucket)
			print(res)
			return {'Bucket': Bucket, 'Key':Key}


