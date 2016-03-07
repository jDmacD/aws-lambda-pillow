module.exports = {
	options: {
		credentials: {
			accessKeyId: '<%= config.accessKeyId %>',
			secretAccessKey: '<%= config.secretAccessKey %>',
			region: '<%= config.region %>'
		},
		dest: 'log/'
	},
	launchEC2Instance: {
		service: 'ec2',
		method: 'runInstances',
		params: {
			ImageId: 'ami-bff32ccc', // http://docs.aws.amazon.com/lambda/latest/dg/current-supported-versions.html
			MinCount: 1,
			MaxCount: 1,
			KeyName: '<%= config.KeyName %>',
			SecurityGroupIds: '<%= config.SecurityGroupIds %>',
			InstanceType: 't2.micro',
			UserData: '<%= userData  %>',
			IamInstanceProfile: {
				Arn: "arn:aws:iam::535915538966:instance-profile/ec2_s3"
			}
		}
	},
	'updateLambda-composite': {
		service: 'lambda',
		method: 'updateFunctionCode',
		params: {
			FunctionName: 'composite',
			S3Bucket: '<%= config.codeBucket %>',
			S3Key: 'lambda/composite.zip'
		}
	},
	'updateLambda-webpConverter': {
		service: 'lambda',
		method: 'updateFunctionCode',
		params: {
			FunctionName: 'webpConverter',
			S3Bucket: '<%= config.codeBucket %>',
			S3Key: 'lambda/webpConverter.zip'
		}
	},
	'updateLambda-svgConverter': {
		service: 'lambda',
		method: 'updateFunctionCode',
		params: {
			FunctionName: 'svgConverter',
			S3Bucket: '<%= config.codeBucket %>',
			S3Key: 'lambda/svgConverter.zip'
		}
	}
}