/* global module: true */
'use strict';

module.exports = function (config) {
  config.set({
    files: [
      'webapp/sportsfronter/static/webapp/js/jquery.min.js',
      'webapp/sportsfronter/static/webapp/js/angular-1.2.9.min.js',
      'webapp/sportsfronter/static/webapp/js/angular-route-1.2.9.min.js',
      'webapp/sportsfronter/static/webapp/js/angular-touch-1.2.9.min.js',
      'webapp/sportsfronter/static/webapp/js/ui-bootstrap-tpls-0.8.0.min.js',
      'webapp/sportsfronter/static/webapp/js/angular-cookies-1.2.9.min.js',
      'webapp/sportsfronter/static/webapp/js/angular-mocks.js',
      'webapp/sportsfronter/static/webapp/js/local_settings.js',
      'webapp/sportsfronter/static/webapp/js/app.js',
      'webapp/sportsfronter/static/webapp/js/controllers/*.js',
      'webapp/sportsfronter/static/webapp/js/services/*.js',
      'webapp/test/unit/**/*.js'
    ],

    exclude: [
      'webapp/sportsfronter/static/webapp/js/cordova/*.js',
      'webapp/sportsfronter/static/webapp/js/ios/*.js'
    ],

    frameworks: ['jasmine'],

    browsers: ['PhantomJS'],

    plugins: [
      'karma-junit-reporter',
      'karma-phantomjs-launcher',
      'karma-jasmine'
    ],

    junitReporter: {
      outputFile: 'dist/unit.xml'
    }
  });
};
