var fs = require('fs-extra');
var path = require('path');
var _ = require('lodash');
var async = require('async');
var JSZip = require('jszip');
var AWS = require('aws-sdk');

module.exports = function(grunt) {
    'use strict';
    // Project configuration
    grunt.initConfig({
        // Metadata
        pkg: grunt.file.readJSON('package.json'),
        banner: '/*! <%= pkg.name %> - v<%= pkg.version %> - ' +
            '<%= grunt.template.today("yyyy-mm-dd") %>\n' +
            '<%= pkg.homepage ? "* " + pkg.homepage + "\\n" : "" %>' +
            '* Copyright (c) <%= grunt.template.today("yyyy") %> <%= pkg.author.name %>;' +
            ' Licensed <%= props.license %> */\n',
        // Task configuration
        config: grunt.file.readJSON('config.json'),
        userData: grunt.file.read('aws/ec2/userData.sh', {
            encoding: 'base64'
        }),
        aws: {
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
            }
        },
        aws_s3: {
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
                    dest: 'env.zip',
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
        },
        'lambda-prep': {
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
                    keepOld:false,
                    format:'webp'
                }
            }
        }
    });

    // These plugins provide necessary tasks
    grunt.loadNpmTasks('grunt-aws-sdk');
    grunt.loadNpmTasks('grunt-aws-s3');
    grunt.loadNpmTasks('grunt-replace');
    // Default task
    grunt.registerTask('default', [
        'lambda-prep:composite',
        'lambda-prep:webpConverter',
        'aws_s3:lambda',
        'aws:updateLambda-composite',
        'aws:updateLambda-webpConverter'
        ]);
    grunt.registerTask('lambda-composite', ['lambda-prep:composite', 'aws_s3:lambda', 'aws:updateLambda-composite']);
    grunt.registerTask('lambda-webpConverter', ['lambda-prep:webpConverter', 'aws_s3:lambda', 'aws:updateLambda-webpConverter']);
    grunt.registerTask('make-env', ['aws:launchEC2Instance']);
    grunt.registerTask('get-env', ['aws_s3:virtenv']);

    grunt.registerMultiTask('lambda-prep', 'prep code for lambda upload', function() {

        var done = this.async();
        var src = this.data.src;
        var dest = this.data.dest;
        var config = this.data.config;

        var envZip = 'env.zip';
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
};