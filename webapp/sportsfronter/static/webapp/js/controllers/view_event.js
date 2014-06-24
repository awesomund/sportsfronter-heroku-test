var app = angular.module('sportsfronter');

app.controller('ViewEventController', function($scope, $http, $location, $timeout, $routeParams, userService) {

	'use strict';
	$scope.total = 0;
	$scope.yes = 0;
	$scope.no = 0;
	$scope.seen = 0;
	$scope.unknown = 0;
	$scope.invitesPending = false;
	$scope.alerts = [];

	var timer;

	$scope.init = function(){
		refreshTable();
		$scope.sortTable('firstName');
	};


	var refreshTable = function(){
		$scope.fetchAttendees();
		timer = $timeout(refreshTable, 20000);
	};


	$scope.closeAlert = function(index){
		$scope.alerts.splice(index, 1);
	};


	$scope.isIos = userService.isIos();


	// TODO: Seperate out and use both here and in rsvp.js
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


	$scope.fetchAttendees = function(){
		var url = REST_API_URL + '/event/' + $routeParams.eventId;
		$http({
			method: 'GET',
			url: url,
			withCredentials: true,
		}).success(function(data){
			if (data.logout) {
				userService.logOut();
				$location.path( '/auth/login' );
			}
			
			$scope.event = data.event;

			// Use native solutions for maps urls for IOS and Android.
			if (userService.isIos()){
				$scope.event.locationUrl = 'maps://?q=' + $scope.event.location;
			} else if (userService.isAndroid()){
				$scope.event.locationUrl = 'geo:0,0?q=' + $scope.event.location;
			} else {
				$scope.event.locationUrl = 'https://maps.google.com/?q='+ $scope.event.location;
			}
			$scope.attendees = data.attendees;
			$scope.coaches = data.coaches;
			for (var i = $scope.coaches.length - 1; i >= 0; i--) {
				$scope.coaches[i].labelClass = setAnswerLabelClass($scope.coaches[i].answerInt);
				$scope.coaches[i].answerText = setAnswerText($scope.coaches[i].answerInt);
			}

			// Show comment icon when the answer is 'no' AND a comment
			// has been written

			if ($scope.attendees.length){
				for (var i = $scope.attendees.length - 1; i >= 0; i--) {
					var invitesPending = true;
					if ($scope.attendees[i].answerInt !== 5) {
						invitesPending = false;
					}
					$scope.invitesPending = invitesPending;
				}
			}
			else {
				$scope.invitesPending = true;
			}

			for (var i = 0; i < $scope.attendees.length; i++){
				if ($scope.attendees[i].comment) {
					$scope.attendees[i].showComment = true;
				}
				else{
					$scope.attendees[i].showComment = false;
				}
				if ($scope.attendees[i].answer === 'Ikke sendt'){
					$scope.attendees[i].showSendLink = true;
				}
				var answerInt = $scope.attendees[i].answerInt;
				$scope.attendees[i].labelClass = setAnswerLabelClass(answerInt);
			}

			hideCommentHeadline($scope.event.info);
			calculateProgressbarPercentages($scope.attendees);

			$scope.userAnswer = data.userAnswerInt;

			if ($scope.userAnswer === 1){
				$('#yes').siblings().removeClass('btn-danger');
				$('#yes').addClass('btn-success');
				$('#yes').addClass('active');
			}
			else if ($scope.userAnswer === 2){
				$('#no').siblings().removeClass('btn-success');
				$('#no').addClass('btn-danger');
				$('#no').addClass('active');
			}
		});
	};


	$scope.sendSingleInvitation = function(attendee){
		attendee.showSendLink = false;

		var data = {
			event_id: $routeParams.eventId,
			player_id: attendee.id,
		};

		$http({
			method: 'POST',
			url: REST_API_URL + '/event/sendsingleinvitation',
			withCredentials: true,
			data: data,
		}).success(function(data, status) {
			$scope.fetchAttendees();
		}).error(function(data, status) {

		});

	};


	$scope.editEvent = function(){
		$location.path('/event/edit/'+$routeParams.eventId);
	};


	var calculateProgressbarPercentages = function(players){
		var total = players.length;
		var yes = 0;
		var no = 0;
		var seen = 0;
		var sent = 0;

		for (var i=0; i<total; i++){
			if (players[i].answerInt === 1){
				yes++;
			} else if(players[i].answerInt === 2){
				no++;
			} else if(players[i].answerInt === 3){
				seen++;
			} else if(players[i].answerInt === 4){
				sent++;
			}
		}

		$scope.yes = yes;
		$scope.no = no;
		$scope.seen = seen;
		$scope.sent = sent;
		$scope.total = yes + no + seen + sent;

		var yes_percentage = yes / $scope.total * 100;
		var no_percentage = no / $scope.total * 100;
		var seen_percentage = seen / $scope.total * 100;
		var sent_percentage = sent / $scope.total * 100;

		$('#progress-attendance .progress-bar-success').width('' + yes_percentage + '%');
		$('#progress-attendance .progress-bar-danger').width('' + no_percentage + '%');
		$('#progress-attendance .progress-bar-warning').width('' + seen_percentage + '%');
		$('#progress-attendance .progress-bar-unknown').width('' + sent_percentage + '%');

		if ($scope.total === $scope.sent) {
			$scope.sent = $scope.sent + " invitasjoner sendt";
			$('#progress-attendance .overlay').css('left', '38%');
		} else {
			$('#progress-attendance .overlay').css('left', '48%');
		}
	};


	var hideCommentHeadline = function(comment){
		if (comment === ''){
			$('.event-comment').hide();
		}
	};


	$scope.sortTable = function(predicate){
		if($scope.predicate === predicate){
			$scope.direction = !$scope.direction;
		}
		
		else{
			$scope.predicate = predicate;
			$scope.direction = false;
		}
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


	$scope.$on('$locationChangeStart', function(){
		$timeout.cancel(timer);
	});


	$scope.onAnswer = function(answer){

		var data = {
			'eventId' : $routeParams.eventId,
			'answer' : answer,
		};

		$http.post(REST_API_URL + '/event/rsvp/coach', data).success(function(data){

			if (parseInt(data.answer, 10) === 1){
				$scope.attendees = data.attendees;
			}
			else {
				$scope.attendees = data.attendees;
			}

			$scope.fetchAttendees();
		});
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


});
