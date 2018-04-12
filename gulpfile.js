/* global require */
/* jshint node:true */

'use strict';

var gulp = require('gulp');

// css
var less = require('gulp-less');
var minifyCss = require('gulp-minify-css');

// js
var uglify = require('gulp-uglify');

// utils
// var rename = require('gulp-rename');
var notify = require('gulp-notify');
var concat = require('gulp-concat');
var gulpif = require('gulp-if');

// set up variabels
var args = require('yargs').argv;
var env = args.env || 'local';

var paths = {
  less: {
    src: ['./application/private/less/app.less'],
    dest: './application/static/css/',
  },
  js: {
    src: ['./application/private/js/**/*.js'],
    dest: './application/static/js/',
  }
};

gulp.task('default', ['less', 'scripts']);
gulp.task('watch', function() {
  gulp.watch(paths.less.src, ['less']);
  gulp.watch(paths.js.src, ['scripts']);
});

gulp.task('less', function() {
  return gulp.src(paths.less.src)
  .pipe(less())
  .pipe(gulp.dest(paths.less.dest))
  .pipe(minifyCss({
    keepSpecialComments: 0
  }))
  .pipe(gulp.dest(paths.less.dest))
  .pipe(notify({ message: 'Styles built' }));
});

gulp.task('scripts', function() {
  return gulp.src(paths.js.src)
  .pipe(concat('app.js'))
  .pipe(gulp.dest(paths.js.dest))
  .pipe(gulpif(env !== 'local', uglify()))
  .pipe(gulp.dest(paths.js.dest))
  .pipe(notify({ message: 'App Script built' }));
});
