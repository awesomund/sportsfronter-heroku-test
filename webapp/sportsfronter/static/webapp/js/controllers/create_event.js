var app = angular.module('sportsfronter');

app.controller('CreateEventController', function($scope, $http, $location, $timeout, $routeParams) {

	$scope.canUseButtons = true;
	$scope.alerts = [];
	$scope.attendees = [];
	$scope.teams = [];
	$scope.loadedPlayers = false;
	$scope.numberOfSentMail = 0;
	$scope.extra_teams_placeholder = "Velg hoved-lag først";
	$scope.extraAttendees = [];
	$scope.extraPlayers = [];
	$scope.checkedValue = true;
	$scope.extraPlayersCheckedValue = false;
	$scope.extraTeamSelected = false;
	$scope.recurringEvent = false;
	$scope.eventId = $routeParams.eventId;
	$scope.reminderTime = 2;
	$scope.useLastSignupDate = false;
	$scope.recurringEventFrequency = 1;
	$scope.disableDates = false;


	var checked = function() {
		for (var i = 0; i< $scope.attendees.length; i++) {
			$scope.attendees[i].attending = $scope.checkedValue;
		}
	};


	var extraPlayerschecked = function() {
		for (var i = 0; i< $scope.extraPlayers.length; i++) {
			$scope.extraPlayers[i].attending = $scope.extraPlayersCheckedValue;
		}
	};


	$scope.$watch('checkedValue', checked);
	$scope.$watch('extraPlayersCheckedValue', extraPlayerschecked);

	$scope.toggleDisable = function(){
		for (var i = 0; i < $scope.teams.length; i++) {
			$scope.teams[i].disabled = false;
			if ($scope.teams[i].id == $scope.team.id) {
				$scope.teams[i].disabled = true;
			}
		}
	};


	$scope.defineExtraTeams = function(){
		$scope.extraTeams = $scope.teams;
		$scope.extraTeamsCheckedValue = true;
		$scope.extra_teams_placeholder = "Velg lag";
	};


	$scope.fetchExtraPlayers = function(){
		$scope.extraTeamSelected = true;
		//var extraTeam = JSON.parse($scope.extraTeam); //WTF, Angular?!
		var extraTeam = $scope.extraTeams[$scope.extraTeamIndex];

		var url = REST_API_URL + '/management/team/' + extraTeam["id"];
		$http({
			method: 'GET',
			url: url,
		}).success(function(extraTeam, status) {
			$scope.extraPlayers = extraTeam.players;
			for (var i = 0; i < $scope.extraPlayers.length; i++) {
				$scope.extraPlayers[i].attending = false;
			}
		}).error(function(data, status) {

		});
	};


	$scope.init = function() {
		initDateTime();
		$scope.submitted = false;
		if ($routeParams.eventId) {
			$scope.isNewEvent = false;
			fetchEvent();
			$scope.fetchTeams();
		}
		else {
			$scope.isNewEvent = true;
			$scope.fetchTeams();
		}
	};


	var initDateTime = function(){
		var date = new Date();
		var coeff = 1000 * 60 * 5;
		var roundedMinuteDate = new Date(Math.round(date.getTime() / coeff) * coeff);
	 
		$scope.date  = date.getDate();
		$scope.month = date.getMonth() + 1;
		$scope.year = parseInt(date.getFullYear(), 10);

		$scope.startHour = date.getHours();
		$scope.startMinute = roundedMinuteDate.getMinutes();

		$scope.meetupTimeOffset = 10; //minutes before start
		$scope.meetupDateTime = new Date(Math.round(date.getTime() / coeff) * coeff);
		$scope.meetupDateTime.setMinutes($scope.meetupDateTime.getMinutes() - $scope.meetupTimeOffset);

		$scope.endHour = date.getHours() + 1;
		$scope.endMinute = roundedMinuteDate.getMinutes();

		$scope.setDates($scope.month, $scope.year);
		$scope.setMonths();
		$scope.setYears($scope.year);
		$scope.setHours();
		$scope.setMinutes();
		$scope.setMeetupMinutes();

		$scope.lastSignupDate  = date.getDate();
		$scope.lastSignupMonth = date.getMonth() + 1;
		$scope.lastSignupYear = parseInt(date.getFullYear(), 10);
		$scope.setLastSignupDates($scope.lastSignupMonth, $scope.lastSignupYear);
		$scope.setLastSignupMonths();
		$scope.setLastSignupYears($scope.lastSignupYear);
		$scope.lastSignupHour = $scope.meetupDateTime.getHours();
		$scope.lastSignupMinute = $scope.meetupDateTime.getMinutes();

		$scope.recurringEventStartDate  = date.getDate();
		$scope.recurringEventStartMonth = date.getMonth() + 1;
		$scope.recurringEventStartYear = parseInt(date.getFullYear(), 10);
		$scope.setRecurringEventStartDates($scope.recurringEventStartMonth, $scope.recurringEventStartYear);
		$scope.setRecurringEventStartMonths();

		$scope.recurringEventEndDate  = date.getDate();
		$scope.recurringEventEndMonth = date.getMonth() + 1;
		$scope.recurringEventEndYear = parseInt(date.getFullYear(), 10);
		$scope.setRecurringEventEndDates($scope.recurringEventEndMonth, $scope.recurringEventEndYear);
		$scope.setRecurringEventEndMonths();

	};


	$scope.fetchAttendees = function() {

		var url = REST_API_URL + '/management/team/' + $scope.team['id'];
		$http({
			method: 'GET',
			url: url,
		}).success(function(team, status) {
			$scope.attendees = team.players;
			$scope.loadedPlayers = true;
			checked();

			for (var i = $scope.attendees.length - 1; i >= 0; i--) {
				$scope.attendees[i].team = $scope.team;
			}
		}).error(function(data, status) {

		});
	};


	$scope.fetchTeams = function () {
		$scope.attendeeList = true;
		$http({
			method: 'GET',
			url: REST_API_URL + '/management/teams',
			withCredentials: true,
		}).success(function(data, status){
			if (data['logout']) {
				userService.logOut();
				$location.path( "/auth/login" );
				return;
			}

			$scope.teams = data;

			for (var i = 0; i < $scope.teams.length; i++) {
				$scope.teams[i].disabled = false;
			}

			if ($routeParams.eventId) {
				$scope.defineExtraTeams();
			}
		}).error(function(data, status) {

		});
	};
 

	var fetchEvent = function() {
		var url = REST_API_URL + '/event/' + $routeParams.eventId;
		$http({
			method: 'GET',
			url: url,
			withCredentials: true,
			}).success(function(data, status) {
				if (data['logout']) {
				userService.logOut();
				$location.path( "/auth/login" );
				return;
				}

				setData(data.event);

				$scope.team = data.event.team;
				$scope.teamIndex = $scope.teams[0];

				var teamPlayers = data['teamPlayers'];
				$scope.eventPlayers = data.attendees;
				$scope.attendees = teamPlayers;

				for (var i = $scope.attendees.length - 1; i >= 0; i--) {
					$scope.attendees[i].team = $scope.team;
				}

				addExtraPlayersToAttendeeList();
				checkAttendingPlayers();

				$scope.loadedPlayers = true;

		}).error(function(data, status) {

		});
	};

	var addExtraPlayersToAttendeeList = function(){
		for (var i = $scope.eventPlayers.length - 1; i >= 0; i--) {

			var extraPlayer = true;

			for (var j = $scope.attendees.length - 1; j >= 0; j--) {
				if ($scope.eventPlayers[i].username === $scope.attendees[j].username) {
					extraPlayer = false;
				}
			}
			if (extraPlayer) {
				$scope.attendees.push($scope.eventPlayers[i]);
			}
		}
	};


	var checkAttendingPlayers = function(){
		//if attendee is in eventPlayers, check attendee
		for (var i = $scope.attendees.length - 1; i >= 0; i--) {
			var attending = false;
			for (var j = $scope.eventPlayers.length - 1; j >= 0; j--) {
				if ($scope.attendees[i].username === $scope.eventPlayers[j].username) {
					attending = true;
				}
			}
			$scope.attendees[i].attending = attending;
		}
	};


	var calculateMinuteDifference = function(startDate, endDate){
		var diff = endDate - startDate;
		var minuteDiff = Math.round(diff/60000);
		return
	};


	var setData = function(data) {
		var eventDate = new Date(data.date);
		var eventMonth = eventDate.getMonth();
		var eventMeetupTimeArray = data.meetupTime.split(":");
		var eventMeetupHour = eventMeetupTimeArray[0];
		var eventMeetupMinute = eventMeetupTimeArray[1];

		var eventStartTimeArray = data.startTime.split(":");
		var eventStartHour = eventStartTimeArray[0];
		var eventStartMinute = eventStartTimeArray[1];

		var eventEndTimeArray = data.endTime.split(":");
		var eventEndHour = eventEndTimeArray[0];
		var eventEndMinute = eventEndTimeArray[1];

		var eventMeetupDateTime = new Date(eventDate.getFullYear(), eventMonth, eventDate.getDate(), eventMeetupHour, eventMeetupMinute);
		var eventStartDateTime = new Date(eventDate.getFullYear(), eventMonth, eventDate.getDate(), eventStartHour, eventStartMinute);
		var eventEndDateTime = new Date(eventDate.getFullYear(), eventMonth, eventDate.getDate(), eventEndHour, eventEndMinute);

		$scope.date  = eventMeetupDateTime.getDate();
		$scope.month = eventMeetupDateTime.getMonth() + 1;
		$scope.year = parseInt(eventMeetupDateTime.getFullYear(), 10);

		$scope.meetupTimeOffset = Math.round((eventStartDateTime-eventMeetupDateTime)/60000);
		$scope.meetupDateTime = eventMeetupDateTime;
		
		$scope.startMinute = eventStartDateTime.getMinutes();
		$scope.startHour= eventStartDateTime.getHours();

		$scope.endMinute = eventEndDateTime.getMinutes();
		$scope.endHour = eventEndDateTime.getHours();

		if (data.lastSignupDate.length) {
			$scope.useLastSignupDate = true;

			var lastSignupDateTime = new Date(data.lastSignupDate);
			$scope.lastSignupDate  = lastSignupDateTime.getDate();
			$scope.lastSignupMonth = lastSignupDateTime.getMonth() + 1;
			$scope.lastSignupYear = parseInt(lastSignupDateTime.getFullYear(), 10);
			var lastSignupTimeArray = data.lastSignupTime.split(':');
			lastSignupDateTime.setHours(lastSignupTimeArray[0]);
			lastSignupDateTime.setMinutes(lastSignupTimeArray[1]);
			$scope.lastSignupHour = lastSignupDateTime.getHours();
			$scope.lastSignupMinute = lastSignupDateTime.getMinutes();
		}
		else {
			$scope.lastSignupDate  = eventMeetupDateTime.getDate();
			$scope.lastSignupMonth = eventMeetupDateTime.getMonth() + 1;
			$scope.lastSignupYear = parseInt(eventMeetupDateTime.getFullYear(), 10);
			$scope.lastSignupHour = eventMeetupDateTime.getHours();
			$scope.lastSignupMinute = eventMeetupDateTime.getMinutes();
		}
		

		$scope.title = data.title;
		$scope.location = data.location;
		$scope.information = data.info;
		$scope.teams = [data.team];
		$scope.opponent = data.opponent;
		$scope.attendees = data.attendees;
		$scope.loadedPlayers = false;
		$scope.team = data.team;
		$scope.reminderTime = data.reminderTime;

		if (data.eventGroup) {
			$scope.recurringEvent = true;
			$scope.eventGroupId = data.eventGroup.id;
			$scope.eventGroupTitle = data.eventGroup.title;
			$scope.editAllEventsInGroup = 1;
			$scope.disableDates = true;
			$scope.$watch('editAllEventsInGroup', function(){
				if (parseInt($scope.editAllEventsInGroup, 10) === 1) {
					$scope.disableDates = true;
				}
				else if(parseInt($scope.editAllEventsInGroup, 10) === 0){
					$scope.disableDates = false;
				}
			});
		}

		$('#teamSelector').val(data.team.id); //do this the angular way...
		$scope.team_id = data.team.id;
	};
	

	var buildEventData = function(){
		var data = {
			title: $scope.title,
			date: $scope.year + '-' + $scope.month + '-' + $scope.date,
			meetupTime: $scope.meetupDateTime.getHours() + ':' + $scope.meetupDateTime.getMinutes(),
			startTime: $scope.startHour+ ':' + $scope.startMinute,
			endTime: $scope.endHour+ ':' + $scope.endMinute,
			location: $scope.location,
			info: $scope.information,
			opponent: $scope.opponent,
			attendees: [],
			notInvited: notInvitedList(),
			extraAttendees: $scope.extraAttendees,
			team: $scope.team.id,
			reminderTime: $scope.reminderTime
		};

		if ($scope.useLastSignupDate) {
			data.lastSignupDate = $scope.lastSignupYear + '-' + $scope.lastSignupMonth + '-' + $scope.lastSignupDate;
			data.lastSignupTime = $scope.lastSignupHour + ':' + $scope.lastSignupMinute;
		}
		else {
			data.lastSignupDate = null;
			data.lastSignupTime = null;
		}

		if ($scope.recurringEvent || $scope.eventGroupId) {
			data.recurringEvent = true;
			data.recurringEventStartDate = $scope.recurringEventStartYear + '-' + $scope.recurringEventStartMonth + '-' + $scope.recurringEventStartDate;
			data.recurringEventEndDate = $scope.recurringEventEndYear + '-' + $scope.recurringEventEndMonth + '-' + $scope.recurringEventEndDate;
			data.recurringEventFrequency = $scope.recurringEventFrequency;
			data.eventGroupTitle = $scope.eventGroupTitle;
		}

		if ($routeParams.eventId) {
			data.eventId = $routeParams.eventId;
		}

		if ($scope.eventGroupId) {
			data.eventGroupId = $scope.eventGroupId;
			data.editAllEventsInGroup = parseInt($scope.editAllEventsInGroup, 10);
		}

		for (var i = $scope.attendees.length - 1; i >= 0; i--) {
			if($scope.attendees[i].attending){
				data.attendees.push($scope.attendees[i]);
			}
		}

		return data;
	};

	$scope.deleteEvent = function(){

		var data = {
			event_id: $routeParams.eventId,
		};

		if ($scope.recurringEvent && $scope.editAllEventsInGroup === 1) {
			if (confirm('Er du sikker på at du vil slette alle arrangement i denne gruppen?')) {
				data.eventGroupId = $scope.eventGroupId;
			}
			else{
				if (!confirm('Vil du slette dette ene arrangementet?')) {
					return;
				}
			}
		}

		$http.post(REST_API_URL + '/event/delete', data).success(function(data, status) {
				$scope.alerts = [{type: 'success', comment: '', msg:'Arrangementet er slettet'}];
				$timeout(redirectToViewEvent, 2000);
			}).error(function(data, status){
				$scope.canUseButtons = true;
				$scope.alerts = [{type: 'warning', comment: 'Serverfeil', msg: "Det har skjedd en feil."}];
			});
	};

	$scope.saveEvent = function(sendNotification, shareEvent) {
		$scope.submitted = true;
		if (!validateSchema()) {
			$scope.alerts = [{type: 'error', comment: 'Obs! ', msg: "Obligatoriske felt må fylles ut."}];
			return;
		}
		
		$scope.alerts = [{type: 'info', comment: 'Sender... ', msg: 'vennligst vent'}];
		
		var requestData = buildEventData();
		requestData.sendNotification = sendNotification;
		requestData.shareEvent = shareEvent;
		
		numberOfSentMail = $scope.attendees.length - notInvitedList().length;

		$http.post(REST_API_URL + '/event/save', requestData)
			.success(function(requestData, status) {
				mixpanel.track("User successfully created event");
				mixpanel.track("User responded to or created event");
				if (sendNotification) {
					$scope.alerts = [{type: 'success', comment: '', msg:'Du har sendt ' + numberOfSentMail + ' invitasjon(er).'}];
				}
				else{
					$scope.alerts = [{type: 'success', comment: '', msg:'Arrangementet er lagret.'}];
				}
				$timeout(redirectToViewEvent, 2000);
			}).error(function(requestData, status){
				mixpanel.track("User encountered error while trying to create event");
				$scope.alerts = [{type: 'warning', comment: 'Serverfeil', msg: "Det har skjedd en feil."}];
			});
	};


	$scope.cancelEventInvite = function() {
		if (confirm('Er du sikker på at du vil avbryte?')) {
			$location.path("/");
		}
	};


	var redirectToViewEvent = function() {
		$scope.canUseButtons = true;
		$location.path("/event/all");
	};


	var validateSchema = function() {
		if (!$scope.information) {
			$scope.information = "";
		}

		if (!$scope.opponent) {
			$scope.opponent = "";
		}

		if(!$scope.title || !$scope.location || !$scope.team) {
			return false;
		}

		return true;
	};

	var notInvitedList = function() {
		var tmpList = [];

		for (var i = 0; i < $scope.attendees.length; i++) {
			if (!$scope.attendees[i].attending) {
				tmpList.push($scope.attendees[i].username);
			}
		}

		return tmpList;
	};

	function dateToYMD(date) {
		var d = date.getDate();
		var m = date.getMonth() + 1;
		var y = date.getFullYear();
		return '' + y + '-' + (m<=9 ? '0' + m : m) + '-' + (d <= 9 ? '0' + d : d);
	}

	$scope.closeAlert = function(index) {
		$scope.alerts.splice(index, 1);
	};

	function daysInMonth(month, year) {
		return new Date(year, month, 0).getDate();
	}
	
	$scope.setDates = function(){
		var num = daysInMonth($scope.month, $scope.year);
		var dates = [];
		for (var i = 0; i < num; i++){
			dates.push(i + 1);
		}
		$scope.dates  = dates;
	};

	$scope.setLastSignupDates = function(){
		var num = daysInMonth($scope.lastSignupMonth, $scope.lastSignupYear);
		var dates = [];
		for (var i = 0; i < num; i++){
			dates.push(i + 1);
		}
		$scope.lastSignupDates  = dates;
	};

	$scope.setRecurringEventStartDates = function(){
		var num = daysInMonth($scope.recurringEventStartMonth, $scope.recurringEventStartYear);
		var dates = [];
		for (var i = 0; i < num; i++){
			dates.push(i + 1);
		}
		$scope.recurringEventStartDates  = dates;
	};

	$scope.setRecurringEventEndDates = function(){
		var num = daysInMonth($scope.recurringEventEndMonth, $scope.recurringEventEndYear);
		var dates = [];
		for (var i = 0; i < num; i++){
			dates.push(i + 1);
		}
		$scope.recurringEventEndDates  = dates;
	};

	$scope.setMonths = function(){
		var months = [];
		for (var i = 0; i < 12; i++){
			months.push(i + 1);
		}
		$scope.months = months;
	};

	$scope.setLastSignupMonths = function(){
		var months = [];
		for (var i = 0; i < 12; i++){
			months.push(i + 1);
		}
		$scope.lastSignupMonths = months;
	};

	$scope.setRecurringEventStartMonths = function(){
		var months = [];
		for (var i = 0; i < 12; i++){
			months.push(i + 1);
		}
		$scope.recurringEventStartMonths = months;
	};

	$scope.setRecurringEventEndMonths = function(){
		var months = [];
		for (var i = 0; i < 12; i++){
			months.push(i + 1);
		}
		$scope.recurringEventEndMonths = months;
	};
	
	$scope.setYears = function(){
		var years = [];
		for (var i = $scope.year; i < $scope.year + 5 ; i++){
			years.push(i);
		}
		$scope.years = years;
	};

	$scope.setLastSignupYears = function(){
		var years = [];
		for (var i = $scope.lastSignupYear; i < $scope.lastSignupYear + 5 ; i++){
			years.push(i);
		}
		$scope.setLastSignupYears = years;
	};

	$scope.setRecurringEventEndYears = function(){
		var years = [];
		for (var i = $scope.setRecurringEventStartYear; i < $scope.setRecurringEventStartYear + 5 ; i++){
			years.push(i);
		}
		$scope.setRecurringEventStartYears = years;
	};

	$scope.setRecurringEventEndYears = function(){
		var years = [];
		for (var i = $scope.setRecurringEventEndYear; i < $scope.setRecurringEventEndYear + 5 ; i++){
			years.push(i);
		}
		$scope.setRecurringEventEndYears = years;
	};

	$scope.setHours = function(){
		var hours = [];
		for (var i = 0; i < 24; i++){
			hours.push(i);
		}
		$scope.hours = hours;
	};

	$scope.setMinutes = function(){
		var minutes = [];
		var interval = 5;
		for (var i = 0; i < 60;i++){
			if( i % interval === 0){
				minutes.push(i);
			}
		}
		$scope.minutes = minutes;
	};

	$scope.setMeetupMinutes = function(){
		var minutes = [];
		var interval = 10;
		for (var i = 0; i < 130;i++){
			if( i % interval === 0){
				minutes.push(i);
			}
		}
		$scope.meetupMinutes = minutes;
	};

	$scope.setMeetupTimeHour = function(){
		$scope.startHour = $scope.hour;
	};
	
	$scope.setMeetupTimeMinute = function(){
		$scope.startMinute = $scope.minute;
	};

	
	$scope.setStartTime = function(){
		var startDate = new Date();
		var endDate = new Date();
		
		endDate.setHours($scope.endHour);
		endDate.setMinutes($scope.endMinute);

		startDate.setHours($scope.startHour);
		startDate.setMinutes($scope.startMinute);

		if(endDate <= startDate){
			$scope.startHour = endDate.getHours() - 1;
			$scope.startMinute = endDate.getMinutes();
		}
	};


	$scope.setEndTime = function(){
		var startDate = new Date();
		var endDate = new Date();
		
		endDate.setHours($scope.endHour);
		endDate.setMinutes($scope.endMinute);

		startDate.setHours($scope.startHour);
		startDate.setMinutes($scope.startMinute);

		if(endDate <= startDate){
			$scope.endHour = startDate.getHours() + 1;
			$scope.endMinute = startDate.getMinutes();
		}
	};


	$scope.setMeetupTime = function(){
		var startDate = new Date();

		startDate.setHours($scope.startHour);
		startDate.setMinutes($scope.startMinute);

		$scope.meetupDateTime.setHours($scope.startHour);
		$scope.meetupDateTime.setMinutes($scope.startMinute - $scope.meetupTimeOffset);setData
	};


	$scope.setLastSignupTime = function(){
		var meetupDateTime = new Date($scope.year, $scope.month, $scope.date, $scope.startHour, $scope.startMinute);
		meetupDateTime.setMinutes($scope.startMinute - $scope.meetupTimeOffset);
		$scope.lastSignupDate = meetupDateTime.getDate();
		$scope.lastSignupMonth = meetupDateTime.getMonth();
		$scope.lastSignupYear = meetupDateTime.getFullYear();
		$scope.lastSignupHour = meetupDateTime.getHours();
		$scope.lastSignupMinute = meetupDateTime.getMinutes();

	};


	$scope.checkLastSignupTime = function(){
		var lastsSignupDateTime = new Date($scope.lastSignupYear, $scope.lastSignupMonth-1, $scope.lastSignupDate, $scope.lastSignupHour, $scope.lastSignupMinute);

		if (lastsSignupDateTime > $scope.meetupDateTime) {
			$scope.lastSignupDate = $scope.meetupDateTime.getDate();
			$scope.lastSignupMonth = $scope.meetupDateTime.getMonth();
			$scope.lastSignupYear = $scope.meetupDateTime.getFullYear();
			$scope.lastSignupHour = $scope.meetupDateTime.getHours();
			$scope.lastSignupMinute = $scope.meetupDateTime.getMinutes();

			$scope.alerts.push({type: 'warning', comment: '', msg: 'Påmeldingsfristen kan ikke være etter oppmøtetiden.'});
		}
	};


	$scope.addRecipient = function(){
		$scope.addRecipientClicked = true;
	};


	$scope.addExtraAttendees = function(){
		
		counter = 0;
		existing_attendee_counter = 0;

		for (var i = 0; i < $scope.extraPlayers.length; i++) {
			var playerAlreadyAdded = false;

			if ($scope.extraPlayers[i].attending === false){
				continue;
			}

			for (var j = 0; j < $scope.attendees.length; j++) {
				if ($scope.extraPlayers[i].username === $scope.attendees[j].username) {
					existing_attendee_counter++;
					playerAlreadyAdded = true;
					continue;
				}
			}
			if (playerAlreadyAdded) {
				continue;
			}
			
			counter++;
			$scope.attendees.push($scope.extraPlayers[i]);

			//Extra attendees need to be handled differently than normal ones backend.
			//Need to include their teams.
			$scope.extraPlayers[i].team = $scope.extraTeams[$scope.extraTeamIndex];
			$scope.extraAttendees.push($scope.extraPlayers[i]);
		}
		if (counter) {
			$scope.alerts.push({type: 'success', comment: '', msg: counter + ' ekstra spiller(e) lagt til mottakerlisten.'});
		}
		if (existing_attendee_counter) {
			$scope.alerts.push({type: 'warning', comment: '', msg: existing_attendee_counter + ' spiller(e) var allerede lagt til mottakerlisten.'});
		}
		if (!counter && !existing_attendee_counter){
			$scope.alerts.push({type: 'warning', comment: '', msg: 'Du må krysse av ekstra spillere for å legge dem til!'});
		}
	};

});


