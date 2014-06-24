var app = angular.module('sportsfronter');

app.controller('GetStartedController', function($rootScope,$scope, $location, $http, $timeout, $cookies) {

	$scope.init = function(){
		$rootScope.init_navbar();
	};
	
});