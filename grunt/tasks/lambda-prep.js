'use strict';

var fs = require('fs-extra');
var JSZip = require('jszip');

module.exports = function(grunt) {

	grunt.registerMultiTask('lambda-prep', 'prep code for lambda upload', function() {

		var done = this.async();
		var src = this.data.src;
		var dest = this.data.dest;
		var config = this.data.config;

		var envZip = 'virtualenv/env.zip';
		var envZipFinal = dest + this.target + '.zip';

		fs.copySync(envZip, envZipFinal);

		fs.readFile(envZipFinal, function(err, data) {
			if (err) {

				throw err;
				done();

			} else {
				var zip = new JSZip(data);
				fs.readFile(src, function(err, data) {
					if (err) {
						throw err;
						done();
					} else {
						zip.file(src.split('/')[1], data);
						zip.file('config.json', JSON.stringify(config))
						var buffer = zip.generate({
							type: "nodebuffer",
							compression: 'DEFLATE'
						});
						fs.writeFile(envZipFinal, buffer, function(err) {
							if (err) {
								throw err;
								done();
							} else {
								grunt.log.ok([envZipFinal + ' zipped']);
								done();
							};

						});
					}
				});
			};
		});

	});
}