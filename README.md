# aws-lambda-pillow

## Description

A set of Lambda functions, implemented using Pillow, to cover day-to-day use cases:

* Resizing
* Format Conversion
* Watermarking
* Composositing
* Meta-Data Manipulation

The Lambda functions are designed to integrate with S3, API Gateway and will eventually include a Cloudformation template.

## Deployment Package

To enable support for the broadest possible spectrum of image formats a virtualenv deployment package is required.

To ensure compability, the virtualenv bundle has been built using the same [Linux AMI](http://docs.aws.amazon.com/lambda/latest/dg/current-supported-versions.html) that Lambda utilises.

## Supported Formats

* JPEG
* TIFF
* PNG


