# aws-lambda-pillow

## Description

A set of Lambda functions, implemented using Pillow, to cover day-to-day use cases:

* Resizing
* Format Conversion
* Watermarking
* Composositing
* Meta-Data Manipulation

The Lambda functions are designed to integrate with S3, API Gateway and will eventually include a Cloudformation template.

## Image Return Modes

At the moment Lambda, and API Gateway, have significant restrictions on what can be returned. As such image are returned two ways:

* 64-bit encoded string (up to 6mb)
* Signed redirect to S3

## Supported Formats

* JPEG
* TIFF
* PNG
* WebP

## Setup

a `config.json` file is required in the root of the project with the following attributes

```json
{
  "accessKeyId": "<YOUR KEY ID>",
  "secretAccessKey": "< YOUR ACCESS KEY>",
  "region": "eu-west-1",
  "KeyName": "<YOUR EC2 pem name>",
  "SecurityGroupIds": [
    "<YOUR EC2 SEC. GROUP ID>"
  ]
}

```

## Deployment Package

To enable support for the broadest possible spectrum of image formats a virtualenv deployment package is required.
To ensure compability, the virtualenv bundle has been built using the same [Linux AMI](http://docs.aws.amazon.com/lambda/latest/dg/current-supported-versions.html) that Lambda utilises.
