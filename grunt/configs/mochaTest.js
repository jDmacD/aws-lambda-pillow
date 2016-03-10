module.exports = {
	test: {
		options: {
			reporter: 'spec',
			quiet: false, // Optionally suppress output to standard out (defaults to false)
			clearRequireCache: true // Optionally clear the require cache before running tests (defaults to false)
		},
		src: ['test/tasks/*.js']
	}
}