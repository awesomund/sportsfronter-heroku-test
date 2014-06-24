var app = angular.module('sportsfronter');

app.controller('GCMController', function($rootScope, $scope, $location, userService) {

	$scope.onMessage = function(e){
		//$scope.gcm_message = e.message + "  " + e.event_id;
		$location.path("/rsvp/" + e.event_id);
		//$rootScope.toEvent(e.event_id);
		//$rootScope.init_events();
	}
});
