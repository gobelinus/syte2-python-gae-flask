/* jshint node: true */
/* global angular:false */

'use strict';

angular
  .module('clientApp', [
    'ngAnimate',
    'ngRoute',
    'ngSanitize',
    'angularMoment',
    'angularModalService',
    'angularLazyImg'
  ])
  .config(function ($routeProvider) {
    $routeProvider
      .when('/', {
        templateUrl: '/partials/stream/index.html',
        controller: 'StreamCtrl'
      })
      .when('/twitter', {
        templateUrl: '/partials/twitter/index.html',
        controller: 'TwitterCtrl'
      })
      .otherwise('/');
  })
  .run(['$rootScope', '$window', 'ModalService', function($rootScope, $window, ModalService) {
    $rootScope.menuOpened = false;
    $rootScope.$on('$routeChangeStart', function() {
      $rootScope.menuOpened = false;
      setTimeout(function() {
        $window.scrollTo(0, 0);
      }, 500);
    });

    $rootScope.openTwitterPost = function(item, index) {
      ModalService.showModal({
        templateUrl: '/partials/twitter/details.html',
        controller: 'TwitterDetailsCtrl',
        inputs: {
          item: item,
          idx: index
        }
      });
    };
  }])
  .directive('mainNav', ['$rootScope', function($rootScope) {
    return {
      restrict: 'E',
      templateUrl: '/partials/nav.html',
      link: function(scope) {
        scope.toggleMenu = function() {
          $rootScope.menuOpened = !$rootScope.menuOpened;
        };
      }
    };
  }])
  .filter('trusted', ['$sce', function ($sce) {
    return function(url) {
        return $sce.trustAsResourceUrl(url);
    };
  }]);
