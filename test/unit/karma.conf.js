// This is a karma config file. For more details see
//   http://karma-runner.github.io/0.13/config/configuration-file.html
// we are also using it with karma-webpack
//   https://github.com/webpack/karma-webpack

var webpackConfig = require('../../build/webpack.test.conf')

module.exports = function (config) {
  config.set({
    // to run in additional browsers:
    // 1. install corresponding karma launcher
    //    http://karma-runner.github.io/0.13/config/browsers.html
    // 2. add it to the `browsers` array below.
    browsers: ['PhantomJS'],
    frameworks: ['mocha', 'sinon-chai', 'phantomjs-shim', 'polyfill'],
    files: ['./index.js'],
    reporters: ['spec', 'coverage', 'junit'],
    preprocessors: {
      './index.js': ['webpack', 'sourcemap']
    },
    polyfill: ['Promise'],
    webpack: webpackConfig,
    webpackMiddleware: {
      noInfo: true
    },
    junitReporter: {
      outputDir: '../../build/reports',
      outputFile: 'junit-karma.xml',
      useBrowserName: true // add browser name to report and classes names
    },
    coverageReporter: {
      dir: '../../build/coverage',
      reporters: [
        { type: 'lcov' },
        // { type: 'cobertura', file: 'cobertura-karma.xml', useBrowserName: true },
        { type: 'text-summary' }
      ]
    }
  })
}