var app = angular.module('sportsfronter');

app.controller('AddPlayerController', function($scope, $location, $http, $routeParams, $timeout, $route, userService) {

	'use strict';

	$scope.init = function(){
		$scope.emailChecked = false;
		$scope.personExists = false;
		$scope.noPlayerEmail = false;
		$scope.userNameGenerated = false;
		$scope.playerAlreadyOnTeam = false;

		$scope.coachId = $routeParams.coachId;
		$scope.teamId = $routeParams.teamId;

		if($scope.coachId){
			fetchCoach();
		}

		$scope.guardians = [];
		$scope.alerts = [];
		
		initDatePicker();
		
	};


	$scope.reset = function(){
		$scope.email = "";
		$scope.firstName = "";
		$scope.lastName = "";
		$scope.phoneNumber = "";
		$scope.init();
		$scope.guardians = [];
	};


	$scope.generateUserName = function(){
		if (!$scope.firstName || !$scope.lastName) {
			$scope.alerts.push({type: 'warning', msg: "", comment: "Husk å fylle inn både fornavn og etternavn."});
			return;
		}

		var url  = REST_API_URL + '/management/person/generate_username?firstName=' + $scope.firstName + '&lastName=' + $scope.lastName;

		$http.get(url, {withCredentials : true
			}).success(function(data, status){

				$scope.email = data.username;
				$scope.userNameGenerated = true;
				$scope.noPlayerEmail = false;

			}).error(function(data, status) {

			});
	};


	$scope.checkEmail = function(event){

		var url  = REST_API_URL + '/management/person/' + $scope.email;

		$http.get(url, {withCredentials : true
			}).success(function(data, status){

				if (data['logout']) {
				userService.logOut();
				$location.path( "/auth/login" );
				return;
				}

				if (!data['person_exists']) {
					$scope.personExists = false;
					$scope.alerts = [];
					return;
				}

				$scope.personExists = true;
				setPlayerData(data);

				teams = data.teams;

				for (var i = teams.length - 1; i >= 0; i--) {
					if (teams[i].team_id == $routeParams.teamId){

						$scope.emailChecked = true;
						$scope.personExists = true;
						$scope.playerAlreadyOnTeam = true;
						setPlayerData(data);
						$scope.alerts.push({type: 'warning', msg: "", comment: "Denne spilleren er allerede registrert på laget."});
						return;
					}
				}

			}).error(function(data, status) {

			});
	};


	var setPlayerData = function(data){
		$scope.firstName = data.first_name;
		$scope.lastName = data.last_name;
		$scope.phoneNumber = data.phone_number;

		if (data.birthdate) {
			birthDate = new Date(data.birthdate);
			$scope.date = birthDate.getDate();
			$scope.month = birthDate.getMonth() + 1;
			$scope.year = birthDate.getFullYear();
		}
	};


	$scope.checkGuardianEmail = function(guardian){

		if (!guardian.email) {
			$scope.alerts.push({type: 'warning', msg: "Du må skrive inn en gyldig email.", comment: ""});
			return;
		}

		var url  = REST_API_URL + '/management/person/' + guardian.email;

		$http.get(url, {withCredentials : true
			}).success(function(data, status){

				if (!data['person_exists']) {
					guardian.personExists = false;
					guardian.emailChecked = true;
				}
				else{
					guardian.personExists = true;
					guardian.emailChecked = true;
					
					guardian.firstName = data.first_name;
					guardian.lastName = data.last_name;
					guardian.phoneNumber = data.phone_number;
				}

			}).error(function(data, status) {

			});
	};


	$scope.savePlayer = function(addMorePlayers){
		if (!$scope.email && !$scope.guardians[0]) {
			$scope.alerts.push({type: 'warning', msg: "", comment: "Spillere uten email må ha minst én foresatt."});
			return;
		}

		for (var i = $scope.guardians.length - 1; i >= 0; i--) {
			if ($scope.email === $scope.guardians[i].email) {
				$scope.alerts.push({type: 'warning', msg: "", comment: "Foresatte og spiller må ha forskjellig email."});
				return;
			}
		}

		$scope.submitted = true;
		if ($scope.addPlayerForm.$valid && $scope.addGuardianForm.$valid){

			var url = REST_API_URL + '/management/team/'+ $scope.teamId + '/player/add';

			var dateOfBirth = "";

			if (!$scope.year || !$scope.month || !$scope.date) {
				dateOfBirth = "";
			}
			else{
				dateOfBirth = $scope.year + "-" + $scope.month + "-" + $scope.date;
			}

			var data = {
				'firstName': $scope.firstName,
				'lastName': $scope.lastName,
				'phoneNumber': $scope.phoneNumber,
				'dateOfBirth': dateOfBirth,
				'email': $scope.email,
				'guardians': $scope.guardians,
				'shirtNumber': $scope.shirtNumber
			};

			$http.post(url, data, {withCredentials: true
			}).success(function(data, status){
				$scope.alerts.push({type: 'success', msg: "Spilleren er registrert!", comment: ""});
				if (addMorePlayers) {
					$timeout(redirectToAddPlayer, 2000);
				}
				else{
					$scope.go('team/' + $scope.teamId);
				}
			}).error(function(data, status) {
				if (data['error_msg']) {
					$scope.alerts.push({type: 'warning', msg: "", comment: data['error_msg']});
				}
				else{
					$scope.alerts.push({type: 'warning', msg: "", comment: "Det har skjedd en feil."});
				}
			});
		}
		else {
			$scope.alerts.push({type: 'warning', msg: "Feltene som er markert er påkrevd", comment: "Husk at minst èn e-postadresse må oppgis"});
			$timeout(clearAlerts, 10000);
		}
	};


	var redirectToAddPlayer = function() {
		$route.reload();
	};

	
	$scope.back = function(){
		$location.path('team/' + $scope.teamId);
	};

	
	$scope.go = function (path) {
		$location.path(path);
	};


	var clearAlerts = function(){
		$scope.alerts = [];
	};


	$scope.closeAlert = function($index) {
		$scope.alerts.splice($index, 1);
	};
	

	$scope.removeGuardian = function($index, id){
		$scope.guardians.splice($index, 1);
		$scope.alerts.push({type: 'warning', msg: "OBS: Husk å lagre for å permanent slette foresatt.", comment: ""});
	};

	
	$scope.addGuardianField = function() {
		var guardian = {'name':"",
					'email':"",
					'phoneNumber':"",
				};

		$scope.guardians.push(guardian);
	};


	$scope.isPlayerEmailRequired = function(){
		if ($scope.guardians.length < 1 || !$scope.addGuardianForm.$valid){
			return true;
		}
		else {
			return false;
		}
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
		return $scope.year + "-" + $scope.month + "-" + $scope.date;
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
