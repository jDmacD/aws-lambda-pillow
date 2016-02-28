var fs = require('fs-extra');
var path = require('path');
var _ = require('lodash');
var async = require('async');
var archiver = require('archiver');

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
        userData: grunt.file.read('userData.sh', {
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
            }
        },
        aws_s3: {
            options: {
                accessKeyId: '<%= config.accessKeyId %>', // Use the variables
                secretAccessKey: '<%= config.secretAccessKey %>', // You can also use env variables
                region: '<%= config.region %>',
                uploadConcurrency: 5, // 5 simultaneous uploads
                downloadConcurrency: 5 // 5 simultaneous downloads 
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
            },
            'lambda-prep':{
                image:{
                    src: 'src/'
                }
            }
        }
    });

    // These plugins provide necessary tasks
    grunt.loadNpmTasks('grunt-aws-sdk');
    grunt.loadNpmTasks('grunt-aws-s3');
    // Default task
    grunt.registerTask('default', ['aws:launchEC2Instance']);

    grunt.registerTask('lambda-prep', 'prep code for lambda upload', function() {

    });
};