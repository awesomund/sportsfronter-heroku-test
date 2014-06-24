var app = angular.module('sportsfronter');

app.controller('ManagementController', function($scope, $location, $http, $routeParams, $timeout, $route, userService) {

	$scope.init = function(){
		$scope.coachId = $routeParams.coachId;
		$scope.playerId = $routeParams.playerId;
		$scope.teamId = $routeParams.teamId;
		$scope.disableEmail = false;
		$scope.fetchTeams();

		$scope.personExists = false;
		$scope.coachAlreadyOnTeam = false;

		if($scope.coachId){
			fetchCoach();
			$scope.personExists = true;
			$scope.disableEmail = true;
		}
		else if($scope.playerId){
			fetchPlayer();
		}

		$scope.guardians = [];
		$scope.alerts = [];
		
		initDatePicker();
		
	};


	$scope.fetchTeams = function () {
		$http({
			method: 'GET',
			url: REST_API_URL + '/management/teams',
			withCredentials: true,
		}).success(function(data){
			if (data.logout) {
				userService.logOut();
				$location.path( '/auth/login' );
				return;
			}
			$scope.teams = data;
			for (var i = $scope.teams.length - 1; i >= 0; i--) {
				if(parseInt($scope.teams[i].id, 10) === parseInt($scope.teamId, 10)){
					$scope.team = $scope.teams[i];
				}
			}
		});
	};


	$scope.checkCoachEmail = function(event){

	var url  = REST_API_URL + '/management/person/' + $scope.coach.email;

	$http.get(url, {withCredentials : true
		}).success(function(data, status){

			if (!data['person_exists'] && !data['teams']) {
				$scope.personExists = false;
				$scope.coachAlreadyOnTeam = false;
				$scope.alerts = [];
				return;
			}

			$scope.personExists = true;
			setCoachData(data);

			coach_roles = data.coach_roles;
			for (var i = coach_roles.length - 1; i >= 0; i--) {
				if (coach_roles[i] == $routeParams.teamId){

					$scope.emailChecked = true;
					$scope.personExists = true;
					$scope.coachAlreadyOnTeam = true;
					setCoachData(data);
					$scope.alerts.push({type: 'warning', msg: "", comment: "Denne personen er allerede lagleder."});
					return;
				}
			}

		}).error(function(data, status) {

		});
	};


	$scope.checkGuardianEmail = function(guardian){

		if (!guardian.email) {
			$scope.alerts.push({type: 'warning', msg: "Du må skrive inn en gyldig email.", comment: ""});
			return;
		}

		var url  = REST_API_URL + '/management/person/' + guardian.email;

		$http.get(url, {withCredentials : true
			}).success(function(data, status){
				if (data['logout']) {
				userService.logOut();
				$location.path( "/auth/login" );
				return;
				}

				if (!data['person_exists']) {
					guardian.personExists = false;
				}
				else{
					guardian.personExists = true;
					
					guardian.firstName = data.first_name;
					guardian.lastName = data.last_name;
					guardian.phoneNumber = data.phone_number;
				}

			}).error(function(data, status) {

			});
	};


	var setCoachData = function(data){
		$scope.coach.firstName = data.first_name;
		$scope.coach.lastName = data.last_name;
		$scope.coach.phoneNumber = data.phone_number;
	};


	var fetchPlayer = function(){
		var url  = REST_API_URL + '/management/player/' + $scope.playerId;
		$http.get(url, {withCredentials : true
			}).success(function (player, status) {
				if (player['logout']) {
				userService.logOut();
				$location.path( "/auth/login" );
				return;
				}

				$scope.player = player;
				$scope.guardians = player.guardians;

				for (var i = player.guardians.length - 1; i >= 0; i--) {
					player.guardians[i].personExists = true;
				}

				setDateOfBirth(player.dateOfBirth);
			}).error(function(data, status) {

			});
	};


	$scope.addPlayerAsCoach = function(){
		var url = REST_API_URL + '/management/team/'+ $scope.teamId +'/coach/add/' + $scope.playerId;
		$http.get(url, {withCredentials : true
			}).success(function (player, status) {
				$scope.player = player;
				$scope.back();
			}).error(function(data, status) {

			});
	};


	$scope.removeAsPlayer = function(){
		var url = REST_API_URL + '/management/player/'+ $scope.playerId +'/remove/';
		$http.get(url, {withCredentials : true
			}).success(function (data, status) {
				$scope.back();
			}).error(function(data, status) {

			});
	};

	
	var fetchCoach = function(){
		var url  = REST_API_URL + '/management/team/'+ $scope.teamId + '/coach/' + $scope.coachId;
		$http.get(url, {withCredentials : true
			}).success(function (data, status) {
				$scope.coach = data;
			}).error(function(data, status) {

			});
	};

	
	$scope.removeAsCoach = function(){
		var url = REST_API_URL + '/management/team/'+ $scope.teamId + '/coach/remove';

		$http.post(url, $scope.coach, { withCredentials: true
			}).success(function(data, status){
				$scope.back();
			}).error(function(data, status) {

			});
	};


	$scope.coachAsPlayer = function(){
		var url = REST_API_URL + '/management/team/' + $scope.teamId + '/player/add/';
		$http.post(url, $scope.coach, {withCredentials: true
			}).success(function(data, status){
				$scope.back();
			}).error(function(data, status) {

			});
	};


	$scope.savePlayer = function(){
		$scope.submitted = true;
		if ($scope.addPlayerForm.$valid && $scope.addGuardianForm.$valid){

			var url = REST_API_URL + '/management/player/' + $scope.player.id + '/update/';

			$scope.player.guardians = $scope.guardians;
			if ($scope.year && $scope.month && $scope.date) {
				$scope.player.dateOfBirth = $scope.year + "-" + $scope.month + "-" + $scope.date;
			}
			else{
				$scope.player.dateOfBirth = null;
			}

			$scope.player.teamId = $scope.team.id;

			$http.post(url, $scope.player, {withCredentials: true
			}).success(function(data, status){
				$scope.alerts.push({type: 'success', msg: "Spilleren er oppdatert!", comment: ""});
				$scope.go('team/' + $scope.teamId);
			}).error(function(data, status) {
				$scope.alerts.push({type: 'warning', msg: "", comment: "Serverfeil"});
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


	$scope.saveCoach = function(redirectpath){
		$scope.submitted = true;
		if ($scope.addCoachForm.$valid){
			var url = REST_API_URL + '/management/team/' + $scope.teamId + '/coach/add';
			$http.post(url, $scope.coach, {withCredentials: true
			}).success(function(data, status){
				$scope.go('team/' + $scope.teamId + redirectpath);
			}).error(function(data, status) {
			});
		}
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
		$scope.guardians.push({'name':"", 'email':"", 'phone_number':""});
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
		date = new Date();
		day = date.getDate();
		month = date.getMonth() + 1;
		year = parseInt(date.getFullYear(), 10);

		setDaysInMonth(month, year);
		setMonths();
		setYears(year);

		$scope.date = day;
		$scope.month = month;
		$scope.year = year;
	};


	var setDateOfBirth = function(date){
		var tempDate = new Date(date);
		$scope.date = tempDate.getDate();
		$scope.month = tempDate.getMonth() + 1;
		$scope.year = parseInt(tempDate.getFullYear(), 10);
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
