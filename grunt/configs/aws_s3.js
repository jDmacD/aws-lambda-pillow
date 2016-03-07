module.exports = {
	options: {
		accessKeyId: '<%= config.accessKeyId %>',
		secretAccessKey: '<%= config.secretAccessKey %>',
		region: '<%= config.region %>',
		uploadConcurrency: 5, // 5 simultaneous uploads
		downloadConcurrency: 5 // 5 simultaneous downloads 
	},
	virtenv: {
		options: {
			bucket: '<%= config.codeBucket %>',
			differential: false
		},
		files: [{
			cwd: './',
			dest: 'virtualenv/env.zip',
			action: 'download'
		}]
	},
	lambda: {
		options: {
			bucket: '<%= config.codeBucket %>',
			differential: false
		},
		files: [{
			action: 'upload',
			expand: true,
			cwd: 'dist/lambda/',
			src: ['**'],
			dest: 'lambda/'
		}]
	}
}