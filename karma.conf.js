// Karma configuration
// Generated on Mon Apr 13 2015 21:02:00 GMT-0400 (EDT)

module.exports = function(config) {
  config.set({

    // base path that will be used to resolve all patterns (eg. files, exclude)
    basePath: '',


    // frameworks to use
    // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
    frameworks: ['jasmine'],


    // list of files / patterns to load in the browser
    // NOTE: that the order js assets are loaded follows jquery>bootstrap>angular>etc
    files: [
      'ab_tool/**/libraries/jquery-1.10.1.min.js',
      'ab_tool/**/libraries/bootstrap.min.js',
      'ab_tool/**/libraries/angular-1.2.27.min.js',
      'ab_tool/**/libraries/angular-mocks-1.2.27.js',
      'ab_tool/**/libraries/*.js',
      'ab_tool/**/*.js',
      'ab_tool/tests/frontend/**/*.js',
    ],


    // list of files to exclude
    exclude: [
    ],


    // preprocess matching files before serving them to the browser
    // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
    preprocessors: {
    },


    // test results reporter to use
    // possible values: 'dots', 'progress'
    // available reporters: https://npmjs.org/browse/keyword/karma-reporter
    reporters: ['progress'],


    // web server port
    port: 9876,


    // enable / disable colors in the output (reporters and logs)
    colors: true,


    // level of logging
    // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
    logLevel: config.LOG_INFO,


    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: true,


    // start these browsers
    // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
    browsers: ['PhantomJS'],


    // Continuous Integration mode
    // if true, Karma captures browsers, runs the tests and exits
    singleRun: true,

    // NOTE: for jenkins integration, reference http://karma-runner.github.io/0.12/plus/jenkins.html
    //reporters: ['dots', 'junit'],
    //junitReporter: {outputFile: 'test-results.xml'}

  });
};
