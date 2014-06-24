var app = angular.module('sportsfronter');

app.controller('RsvpController', function ($scope, $http, $route, $routeParams, $location,$timeout,userService) {
	var update;
	$scope.init = function(){
		mixpanel.track("User opened event invitation");
		restCall();
	};

	$scope.isIos = userService.isIos();
	$scope.alerts = [];

	// TODO: Seperate out and use both here and in view_event.js
	$scope.createCalendarEvent = function(){
		if (userService.isIos()) {
			var cal = window.plugins.calendarPlugin;

			var onSuccess = function(){
				//console.log('Success when creating calendar event');
			};

			var onError = function(){
				//console.log('Failure when creating calendar event');
			};

			var title = $scope.event.title;
			var location = $scope.event.location;
			var notes = $scope.event.info;
			// Required to be on format "2013-10-27 16:30:00"
			var startDate = $scope.event.date + ' ' + $scope.event.meetupTime + ':00';
			var endDate = $scope.event.date + ' ' + $scope.event.endTime + ':00';

			//cal.createEvent will call native code to add event to ios calendar.
			cal.createEvent(title,location,notes,startDate,endDate, onSuccess, onError);
		}
	};


	var restCall = function(){

		data = {};

		if (userService.isAuth()){
			data = {event_id: $routeParams.eventPlayerHash};
		}
		else {
			data = {hash: $routeParams.eventPlayerHash};
		}

		$http({
			method: 'POST',
			url: REST_API_URL + '/event/rsvpdata/',
			withCredentials: true,
			data: data,
		}).success(function(data, status){
			if(data.event){

				if (data['logout']) {
				userService.logOut();
				$location.path( "/auth/login" );
				return;
				}

				$scope.event = data.event;

				// Use native solutions for maps urls for IOS and Android.
				if (userService.isIos()) {
					$scope.event.locationUrl = "maps://?q=" + $scope.event.location;
				} else if (userService.isAndroid()) {
					$scope.event.locationUrl = "geo:0,0?q=" + $scope.event.location;
				} else {
					$scope.event.locationUrl = "https://maps.google.com/?q=" + $scope.event.location;
				}
				$scope.player = data.player;
				$scope.answer = parseInt($scope.player.answer, 10);
				$scope.attendees = data.event.attendees;
				$scope.newComment = $scope.player.comment;
				$scope.coaches = data.coaches;

				for (var i = $scope.coaches.length - 1; i >= 0; i--) {
					$scope.coaches[i].labelClass = setAnswerLabelClass($scope.coaches[i].answerInt);
					$scope.coaches[i].answerText = setAnswerText($scope.coaches[i].answerInt);
				}

				if ($scope.answer == 1){
					$('#yes').siblings().removeClass('btn-danger');
					$('#yes').addClass('btn-success');
					$('#yes').addClass('active');
				}
				else if ($scope.answer == 2){
					$('#no').siblings().removeClass('btn-success');
					$('#no').addClass('btn-danger');
					$('#no').addClass('active');
				}
			}

		}).error(function(data, status) {
			mixpanel.track("User encountered error while receiving event data");
		});
	};


	var timeOutFunction = function () {
		update = $timeout(restCall, 20000);
	};


	function hideCommentHeadline(comment) {
		if(comment === ""){
			$('.event-comment').hide();
		}
	}


	$scope.closeAlert = function(index) {
		$scope.alerts.splice(index, 1);
	};


	$scope.setAnswerColor = function(index){
		if($scope.attendees[index]['answerInt'] == 1){
			return "label label-success";
		}
		else if($scope.attendees[index]['answerInt'] == 2){
			return "label label-important";
		}
		else if($scope.attendees[index]['answerInt'] == 3){
			return "label label-warning";
		}
		else if($scope.attendees[index]['answerInt'] == 5){
			return "label label-inactive";
		}
		else{
			return "label";
		}
	};


	$('#yes').click(function(){
		$(this).siblings().removeClass('btn-danger');
		$(this).addClass('btn-success');
		$('#reason-input').hide();
	});


	$('#no').click(function(){
		$(this).siblings().removeClass('btn-success');
		$(this).addClass('btn-danger');
	});


	$scope.onAnswer = function(answer){

		data = {
			'event_player_id' : $scope.player.event_player_id,
			'answer' : answer,
		};

		$http.post(REST_API_URL + '/event/rsvp', data).success(function(data, status){

			mixpanel.track('User responded to event');
			mixpanel.track('User responded to or created event');

			if (data.answer === 1){
				$scope.alerts.push({type: 'success', msg: 'Du er nå meldt på!'});
			}
			else {
				$scope.alerts.push({type: 'success', msg: 'Du er nå meldt av!'});
			}

			$scope.attendees = data.attendees;
			$scope.coaches = data.coaches;
			for (var i = $scope.coaches.length - 1; i >= 0; i--) {
				$scope.coaches[i].labelClass = setAnswerLabelClass($scope.coaches[i].answerInt);
				$scope.coaches[i].answerText = setAnswerText($scope.coaches[i].answerInt);
			}
		});
	};


	$scope.$on('$locationChangeStart', function(){
		$timeout.cancel(update);
	});


	$scope.updateComment = function () {
		mixpanel.track("User commented on event");
		data = {
			'event_player_id' : $scope.player.event_player_id,
			'comment' : $scope.newComment ,
		};
		$http.post(REST_API_URL + '/event/rsvp', data)
			.success(function(data, status){
				$scope.alerts.push({type: 'success', msg: "Din kommentar er sendt: ", 'comment' : data.comment });
		});
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


	var setAnswerText = function(answerInt){
		switch (answerInt){
			case 1:
				return 'Ja';
			case 2:
				return 'Nei';
			case 3:
				return 'Sett';
			case 4:
				return 'Sendt';
			case 5:
				return 'Ikke Sendt';
		}
	};


});


