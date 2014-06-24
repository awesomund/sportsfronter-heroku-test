var app = angular.module('sportsfronter');

app.controller('InviteLinkNewPlayerController', function($scope, $location, $http, $routeParams, $rootScope, userService) {

	'use strict';

	$rootScope.init_navbar();
	$scope.alerts = []

	$scope.player = {
		firstName: '',
		lastName: '',
		phoneNumber: ''
	};


	$scope.init = function(){
		$scope.newUserRoles = userService.getNewUserRoles();
		$scope.teamId = $routeParams.teamId;
		$scope.showExistingPlayersForm = false;
		fetchTeam();
		initDatePicker();	
	};


	$scope.continue = function(){
		$scope.showExistingPlayersForm = true;
	};


	$scope.finish = function(){

		if ($scope.newUserRoles) {
			var data = $scope.newUserRoles;
			$http({
				method: 'POST',
				url: REST_API_URL + '/management/team/' + $scope.teamId + '/join',
				data: data,
				withCredentials: true,
			}).success(function() {

				$scope.alerts.push({type: 'success', msg: '', comment: 'Du er nå med på laget!'});
				fetchTeam();

			}).error(function(data){

				if (data.errorMessage) {
					$scope.alerts.push({type: 'warning', msg: '', comment: data.errorMessage});
				}
				else {
					$scope.alerts.push({type: 'warning', msg: '', comment: 'Det har skjedd en feil.'});
				}

			});
		}

		if ($scope.newUserRoles.guardian) {
			$location.path('/register/guardian/addplayers/' + $scope.teamId);
			return;
		}

		$location.path('/register/complete/' + $scope.teamId);
	};


	var fetchTeam  = function(){
		var url = REST_API_URL + '/management/team/' + $scope.teamId;
		$http({
			method: 'GET',
			url: url,
			withCredentials: true,
		}).success(function(team) {
			$scope.teamName = team.name;
			$scope.teamPlayers = team.players;
			$scope.coaches = team.coaches;

			$scope.existingPlayers = [];

			for (var i = $scope.teamPlayers.length - 1; i >= 0; i--) {
				var teamPlayerName = $scope.teamPlayers[i].firstName + ' ' + $scope.teamPlayers[i].lastName;
				var teamPlayerUserName = $scope.teamPlayers[i].username;

				if ( teamPlayerName == $rootScope.name && teamPlayerUserName != $rootScope.userName && teamPlayerUserName.indexOf('@sportsfronter.no') > -1) {
					$scope.existingPlayers.push($scope.teamPlayers[i]);
				}
			}

			if ($scope.existingPlayers.length) {
				$scope.showExistingPlayersForm = true;
			}
			else {
				$scope.showExistingPlayersForm = false;
			}

		});
	};


	$scope.mergePlayer = function(existingPlayer){

		clearAlerts();

		var data = {
			oldUserName: existingPlayer.username,
			newUserName: $rootScope.userName
		};

		var url = REST_API_URL + '/management/team/' + $scope.teamId + '/mergeplayers';

		$http({
			method: 'POST',
			url: url,
			data: data,
			withCredentials: true,
		}).success(function() {

			fetchTeam();
			if (!$scope.existingPlayers.length) {
				$scope.showExistingPlayersForm = false;
			}

		}).error(function(){

			$scope.alerts.push({type: 'warning', msg: '', comment: 'Det har skjedd en feil.'});

		});
	};


	$scope.removeExistingPlayerFromList = function($index) {
		$scope.existingPlayers.splice($index, 1);
		if (!$scope.existingPlayers.length) {
			$scope.showExistingPlayersForm = false;
		}
	};


	var clearAlerts = function(){
		$scope.alerts = [];
	};


	var initDatePicker = function(){
		var date = new Date();
		var month = date.getMonth() + 1;
		var year = parseInt(date.getFullYear(), 10);

		setDaysInMonth(month, year);
		setMonths();
		setYears(year);
	};


	var getFormattedDate = function(){
		if (!$scope.year || !$scope.month || !$scope.date) {
			return '';
		}
		return $scope.year + '-' + $scope.month + '-' + $scope.date;
	};


	var daysInMonth = function(month, year) {
		return new Date(year, month, 0).getDate();
	};

	
	var setDaysInMonth = function(month, year){
		var num = daysInMonth(month, year);
		var dates = [];
		for (var i = 0; i < num; i++){
			dates.push(i + 1);
		}
		$scope.dates  = dates;
	};


	var setMonths = function(){
		var months = [];
		for (var i = 0; i < 12; i++){
			months.push(i + 1);
		}
		$scope.months = months;
	};

	
	var setYears = function(year){
		var years = [];
		for (var i = year - 60 ; i  <= year; i++){
			years.push(i);
		}
		$scope.years = years;
	};

});
