var app = angular.module('sportsfronter');

app.controller('GuardianAddPlayerController', function($scope, $location, $http, $routeParams, $rootScope, userService) {

	'use strict';

	$rootScope.init_navbar();

	$scope.guardianPlayers = [];
	$scope.newGuardianPlayers = [];
	$scope.showNewGuardianPlayerForm = false;
	$scope.playerAlreadyExists = false;
	$scope.showConnectToPlayerWindow = false;
	$scope.showExistingPlayersForm = false;
	$scope.guardianRegistered = false;
	$scope.newGuardianPlayer = {
		firstName: '',
		lastName: '',
		phoneNumber: ''
	};


	$scope.init = function(){
		$scope.teamId = $routeParams.teamId;
		$scope.newGuardian = $routeParams.newguardian;
		$scope.guardians = [];
		$scope.alerts = [];
		
		fetchTeam();
		initDatePicker();
		
	};


	$scope.finish = function(){
		userService.determineUserPrivileges();
		$location.path('/register/complete/' + $scope.teamId);
	};


	$scope.selectPlayer = function(player){
		$scope.showConnectToPlayerWindow = true;
		$scope.selectedPlayer = player;

		var dateOfBirth = new Date(player.dateOfBirth);
		$scope.date = dateOfBirth.getDate();
		$scope.month = dateOfBirth.getMonth() + 1;
		$scope.year = dateOfBirth.getFullYear();
	};


	$scope.connectGuardianToPlayer = function(player){
		var url = REST_API_URL + '/management/team/' + $scope.teamId + '/guardian_connect_to_player';
		var data = {
			teamId: $scope.teamId,
			playerUserName: player.username,
			playerPhoneNumber: player.phoneNumber,
			playerBirthDate: getFormattedDate()
		};

		$http({
			method: 'POST',
			url: url,
			data: data,
			withCredentials: true,
		}).success(function() {

			fetchTeam();
			$scope.showConnectToPlayerWindow = false;
			$scope.showExistingPlayersForm = false;
			$scope.showNewGuardianPlayerForm = false;
			$scope.newGuardianPlayer = {};
			$scope.date = null;
			$scope.month = null;
			$scope.year = null;
			$scope.guardianRegistered = true;

			$scope.alerts.push({type: 'success', msg: '', comment: 'Du har blitt knyttet til ' + player.firstName + ' ' + player.lastName + '!'});


		}).error(function(){

			$scope.alerts.push({type: 'warning', msg: '', comment: 'Det har skjedd en feil.'});

		});

		$scope.showConnectToPlayerWindow = false;
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
		});
	};


	$scope.saveNewGuardianPlayer = function(playerIsChecked){

		clearAlerts();

		if ( !$scope.newGuardianPlayer.firstName || !$scope.newGuardianPlayer.lastName) {
			$scope.alerts.push({type: 'warning', msg: '', comment: 'Du må fylle inn fornavn og etternavn på spilleren.'});
			return;
		}

		if ( !$scope.date || !$scope.month || !$scope.year) {
			$scope.alerts.push({type: 'warning', msg: '', comment: 'Du må fylle inn fødselsdato på spilleren.'});
			return;
		}

		var data = $scope.newGuardianPlayer;
		data.newGuardian = true;
		data.dateOfBirth = getFormattedDate();
		data.playerIsChecked = playerIsChecked;

		var url = REST_API_URL + '/management/team/' + $scope.teamId + '/guardian_add_player';

		$http({
			method: 'POST',
			url: url,
			data: data,
			withCredentials: true,
		}).success(function(data) {

			if (data.existingPlayers) {
				$scope.existingPlayers = data.existingPlayers;
				$scope.showExistingPlayersForm = true;
				return;
			}

			$scope.alerts.push({type: 'success', msg: '', comment: 'Du har lagt til ' + $scope.newGuardianPlayer.firstName + ' ' + $scope.newGuardianPlayer.lastName + '!'});

			fetchTeam();
			$scope.showConnectToPlayerWindow = false;
			$scope.showExistingPlayersForm = false;
			$scope.showNewGuardianPlayerForm = false;
			$scope.newGuardianPlayer = {};
			$scope.date = null;
			$scope.month = null;
			$scope.year = null;
			$scope.guardianRegistered = true;

		}).error(function(){

			$scope.alerts.push({type: 'warning', msg: '', comment: 'Det har skjedd en feil.'});

		});
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
