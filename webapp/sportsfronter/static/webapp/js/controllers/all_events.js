var app = angular.module('sportsfronter');

app.controller('allEventsController', function($rootScope,$scope, $location, $http, $timeout, $cookies, userService) {

	$scope.coachEvents = [];
	$scope.playerEvents =[];
	$scope.guardianEvents = [];
	$scope.noCoachEvents = false;
	$scope.notInvitedToAnyEvents = false;
	$scope.noGuardianEvents = false;


	var addeDateTimeObjects = function(events){
		for (var i = events.length - 1; i >= 0; i--) {
			var eventDateTime = new Date(events[i].date);
			var timeArray = events[i].meetupTime.split(':');
			var hours = timeArray[0];
			var minutes = timeArray[1];
			eventDateTime.setHours(hours);
			eventDateTime.setMinutes(minutes);
			events[i].eventDateTime = eventDateTime;
		}
	};
	

	$scope.init = function(){
		$rootScope.init_navbar();

		fetchPlayerEvent();
		fetchCoachEvent();
		fetchGuardianEvents();

		$scope.hasTeam = userService.hasTeam();
		$scope.kake = $cookies.authcookie;
	};


	$scope.noEvents = function(){
		if ($scope.noGuardianEvents && $scope.noCoachEvents && $scope.notInvitedToAnyEvents) {
			return true;
		}
	};


	var fetchGuardianEvents = function(){
		$http({
			method: 'GET',
			url: REST_API_URL + '/event/returnEventsGuardian',
			withCredentials: true,
		}).success(function(data){

			if (data.logout) {
				userService.logOut();
				$location.path( '/auth/login' );
				return;
			}

			$scope.guardianEvents = data;

			for (var i = $scope.guardianEvents.length - 1; i >= 0; i--) {
				var answerInt = $scope.guardianEvents[i].playerAnswerInt;
				$scope.guardianEvents[i].labelClass = setAnswerLabelClass(answerInt);
			}

			if ($scope.guardianEvents.length === 0) {
				$scope.noGuardianEvents = true;
			}
			else {
				$scope.noGuardianEvents = false;
			}

			addeDateTimeObjects($scope.guardianEvents);
			stripYearFromEventDates($scope.guardianEvents);

		});
	};


	var fetchPlayerEvent = function(){
		$http({
			method: 'GET',
			url: REST_API_URL + '/event/returnEventsPlayer',
			withCredentials: true,
		}).success(function(data){
			if (data.logout) {
				userService.logOut();
				$location.path( '/auth/login' );
				return;
			}

			$scope.playerEvents = data;

			for (var i = $scope.playerEvents.length - 1; i >= 0; i--) {
				var answerInt = $scope.playerEvents[i].answerInt;
				$scope.playerEvents[i].labelClass = setAnswerLabelClass(answerInt);
			}

			if ($scope.playerEvents.length === 0) {
				$scope.notInvitedToAnyEvents = true;
			}
			else{
				$scope.notInvitedToAnyEvents = false;
			}

			addeDateTimeObjects($scope.playerEvents);
			stripYearFromEventDates($scope.playerEvents);

		});
	};


	var fetchCoachEvent = function(){
		$http({
			method: 'GET',
			url: REST_API_URL + '/event/returnEventsCoach',
			withCredentials: true,
		}).success(function(data){
			if (data.logout) {
				userService.logOut();
				$location.path( '/auth/login' );
				return;
			}

			$scope.coachEvents = data;

			if ($scope.coachEvents.length === 0) {
				$scope.noCoachEvents = true;
			}
			else {
				$scope.noCoachEvents = false;
			}

			addeDateTimeObjects($scope.coachEvents);
			//sortOutExpiredEvents($scope.coachEvents);
			stripYearFromEventDates($scope.coachEvents);

		});
	};


	var stripYearFromEventDates = function(events) {
		for (var i = 0; i < events.length; i++) {
			var newDateStringArray = events[i].date.split('-');
			events[i].date = newDateStringArray[2] + '/' + newDateStringArray[1];
		}
	};


	var dateToYMD = function(date) {
		var d = date.getDate();
		var m = date.getMonth() + 1;
		var y = date.getFullYear();
		return '' + y + '-' + (m<=9 ? '0' + m : m) + '-' + (d <= 9 ? '0' + d : d);
	};

	
	$scope.createNewEvent = function() {
		$location.path('/event/create');
	};


	$scope.redirectToRSVP = function(eventId) {
		$location.path('/rsvp/' + eventId);
	};


	$scope.redirectToRSVPHash = function(urlHash) {
		$location.path('/rsvp/' + urlHash);
	};


	$scope.redirectToEvent = function(eventId) {
		$location.path('/event/' + eventId);
	};


	var setAnswerLabelClass = function(answerInt){
		switch (answerInt){
		case 1:
			return 'label label-success';
		case 2:
			return 'label label-important';
		case 3:
			return 'label label-warning';
		case 4:
			return 'label';
		case 5:
			return 'label label-inactive';
		}
	};

});
