var path = require('path');
var _ = require('lodash');
var async = require('async');
var AWS = require('aws-sdk');

module.exports = function(grunt) {
    'use strict';
    //Load Task Configurations
    require('load-grunt-config')(grunt, {
        configPath: path.join(process.cwd(), 'grunt', 'configs'),
        data: {
            config: grunt.file.readJSON('config.json'),
            userData: grunt.file.read('aws/ec2/userData.sh', {
                encoding: 'base64'
            })
        }
    });
    //Load NPM Tasks
    require('load-grunt-tasks')(grunt);
    //Load Custom Tasks
    grunt.loadTasks(path.join(process.cwd(), 'grunt', 'tasks'));
    
    grunt.registerTask('default', [
        'lambda-prep:composite',
        'lambda-prep:webpConverter',
        'aws_s3:lambda',
        'aws:updateLambda-composite',
        'aws:updateLambda-webpConverter'
    ]);
    grunt.registerTask('lambda-composite', ['lambda-prep:composite', 'aws_s3:lambda', 'aws:updateLambda-composite']);
    grunt.registerTask('lambda-webpConverter', ['lambda-prep:webpConverter', 'aws_s3:lambda', 'aws:updateLambda-webpConverter']);
    grunt.registerTask('lambda-svgConverter', ['lambda-prep:svgConverter', 'aws_s3:lambda', 'aws:updateLambda-svgConverter']);
    grunt.registerTask('make-env', ['aws:launchEC2Instance']);
    grunt.registerTask('get-env', ['aws_s3:virtenv']);
};