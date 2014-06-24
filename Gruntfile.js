/*global module: true */
'use strict';

module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
    watch: {
      js: {
        files: [
          'webapp/sportsfronter/static/**/*.js',
          'webapp/sportsfronter/static/**/*.html',
          'webapp/test/**/*.js'
        ],
        tasks: ['karma:watch:run', 'jshint']
      },
      tests: {
        files: ['webapp/sportsfronter/test/**/*.js'],
        tasks: ['karma:watch:run']
      }
    },
    jshint: {
      gruntfile: {
        options: {
          jshintrc: '.jshintrc'
        },
        src: 'Gruntfile.js'
      },
      src: {
        options: {
          jshintrc: '.jshintrc'
        },
        src: [
          'webapp/test/**/*.js',
          '!webapp/**/angular*.js'
        ]
      }
    },
    karma: {
      unit: {
        configFile: 'karma.conf.js',
        reporters: ['dots', 'junit'],
        singleRun: true
      },
      watch: {
        configFile: 'karma.conf.js',
        reporters: ['dots'],
        singleRun: false,
        background: true
      }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-karma');

  grunt.registerTask('run', ['karma:watch', 'watch', 'jshint:src', 'jshint:gruntfile']);
  grunt.registerTask('test', ['karma:unit']);
};

