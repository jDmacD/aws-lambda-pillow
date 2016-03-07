module.exports = {
	composite: {
		src: 'src/app.py',
		dest: 'dist/lambda/',
		config: {
			bucket_in: '<%= config.imageBucket %>',
			bucket_out: '<%= config.imageBucket %>'
		}
	},
	webpConverter: {
		src: 'src/app.py',
		dest: 'dist/lambda/',
		config: {
			keepOld: false,
			format: 'webp'
		}
	},
	svgConverter: {
		src: 'src/svg.py',
		dest: 'dist/lambda/',
		config: {
			foo: false,
			bar: 'webp'
		}
	}
}