var should = require('chai').should();
var expect = require('chai').expect;

var _ = require('lodash');

var creds = {
	accessKeyId: process.env.AWS_KEY,
	secretAccessKey: process.env.AWS_SECRET,
	region: process.env.AWS_REGION
};

var AWS = require('aws-sdk');

var lambda = new AWS.Lambda(creds);
var s3 = new AWS.S3(creds);


function invokeLambda(params, callback) {
	lambda.invoke(params, function(err, res) {
		callback(err, res)
	});
};

function listS3(params, callback) {
	s3.listObjects(params, function(err, res) {
		callback(err, res)
	});
}

describe('composite', function() {

	before(function (done) {
		listS3({
			Bucket:'components.jdmacd',
			Delimiter: '/',
			Prefix: 'back/'
		},function(err, res) {
			if (err) {
				done(err)
			} else {
				console.log(res)
				done()
			}
		})
	});

	describe('absolute pixels', function() {

		var data = {};

		before(function (done) {

			invokeLambda({},function(err, res) {
				if (err) {
					done(err);
				} else {
					data = res;
					done();
				}
			})
			
		});

		it('should do what...', function (done) {
			done()
		});
		
	});
	
});