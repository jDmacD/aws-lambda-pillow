# aws-lambda-pillow

## Description

A toolkit of Lambda functions, implemented using Pillow, to cover day-to-day use cases:

* Resizing
* Format Conversion
* Watermarking
* Composositing
* Meta-Data Manipulation

The Lambda functions are designed to integrate with S3, API Gateway and will eventually include a Cloudformation template.

## Image Return Modes

At the moment Lambda, and API Gateway, have significant restrictions on what can be returned. As such the are several options:

* 64-bit encoded string (up to 6mb)
* Signed S3 URL
* JSON: `{"Bucket": "<YOUR IMAGE BUCKET>", "Key":"<YOUR IMAGE KEY>"}`

## Supported Formats

* jpeg
* tiff
* png
* webp
* bmp
* gif

## Setup

a `config.json` file is required in the root of the project with the following attributes

```json
{
  "accessKeyId": "< YOUR KEY ID >",
  "secretAccessKey": "< YOUR ACCESS KEY >",
  "region": "eu-west-1",
  "KeyName": "<YOUR EC2 pem name>",
  "SecurityGroupIds": [
    "<YOUR EC2 SEC. GROUP ID>"
  ],
  "codeBucket":"< YOUR CODE BUCKET >",
  "imageBucket":"< YOUR IMAGE BUCKET >"
}

```

## Virtualenv Bundle

To enable support for the broadest possible spectrum of image formats a virtualenv deployment package is required.
To ensure compability, the virtualenv bundle (env.zip) has been built using the same [Linux AMI](http://docs.aws.amazon.com/lambda/latest/dg/current-supported-versions.html) that Lambda utilises.

The virtualenv bundle (env.zip) in this project includes the following Python packages:

* pillow
* simplejson
* eventlet
* requests

**Warning Boto3 is not included by default**, as it already installed on Lambda.

If you want to enable Boto3 (to test locally for example), or add other pip installable packages and dependencies:

1. Uncomment `pip install --verbose --use-wheel boto3` in [userData.sh](https://github.com/jDmacD/aws-lambda-pillow/blob/master/aws/ec2/userData.sh).
2. Execute `grunt make-env`. This will perform the following actions:
	- Launch an ec2
	- Perform `yum install`s
	- Create a virutalenv
	- Perform `pip install`s
	- Zip `lib` and `lib64` to env.zip
	- Copy env.zip to the codeBucket defined in the `config.json`
3. This operation will take about 5 minutes.
4. Execute `grunt get-env`. This will download the new env.zip, overwriting the original.

