var app = angular.module('sportsfronter');

app.controller('SignupController', function($rootScope,$scope, $http, $location, $routeParams, userService){

	'use strict';

	if ($rootScope.joinTeamRoles) {
		$rootScope.joinTeamRoles = null;
	}

	$scope.signupUrl = userService.getSignupUrl();

	$scope.alerts = [];
	$scope.teamId = $routeParams.teamId;
	$scope.coachName = null;
	$scope.headLine = '';
	$scope.secondaryText = '';
	$scope.modeSelected = false;
	$scope.forgotPasswordURL = REST_API_URL + "/admin/password_reset/";

	$scope.userRoles = {
		player: false,
		guardian: false,
		manager: false
	};


	$scope.finish = function(){
		if ($scope.newUser) {
			$scope.register();
		}
		else {
			$scope.firstLogin();
		}
	};

	var fetchTeam  =  function(){
		var url = REST_API_URL + '/management/team/' + $scope.teamId;
		$http({
			method: 'GET',
			url: url,
			withCredentials: true,
		}).success(function(team) {
			$scope.teamName = team.name;
		});
	};


	if ($scope.teamId) {
		fetchTeam();
		var url = $location.absUrl();
		if (url.indexOf('invite/team/') > -1) {
			userService.setSignupUrl($location.absUrl());
		}
	}
	
	if ($routeParams.coach) {
		$scope.coachName = $routeParams.coach.replace('+', ' ');
	}

	if (!$scope.teamId) {
		$scope.newUser = true;
	}


	$scope.goToRegisterPage = function(){
		$scope.newUser = true;
		$scope.modeSelected = true;
	};


	$scope.goToLoginPage = function(){
		if ($scope.teamId) {
			$scope.newUser = false;
			$scope.modeSelected = true;
		}
		else {
			$location.path('/auth/login/');
		}
	};


	$scope.finish = function(){
		if ($scope.newUser) {
			$scope.register();
		}
		else {
			$scope.firstLogin();
		}
	};


	$scope.init = function(){
		$rootScope.init_navbar();
		mixpanel.track('User viewed signup page');
	};

	$scope.closeAlert = function(index){
			$scope.alerts.splice(index, 1);
	};

	$scope.register = function(){

		if ($scope.newUser) {
			if ($scope.username !== $scope.username2) {
				$scope.alerts.push({type: 'warning', msg: 'Epostene du skrev er ikke like!'});
				return;
			}

			if ($scope.password !== $scope.password2) {
				$scope.alerts.push({type: 'warning', msg: 'Passordene du skrev er ikke like!'});
				return;
			}

			if(!$scope.username || !$scope.username2 || !$scope.password || !$scope.password2 || !$scope.firstName || !$scope.lastName){
				$scope.alerts.push({type: 'warning', msg: 'Brukernavn, navn eller passord er ikke riktig fylt inn.'});
				return;
			}
		}
		else {
			if(!$scope.username || !$scope.password){
				$scope.alerts.push({type: 'warning', msg: 'Brukernavn eller passord er ikke riktig fylt inn.'});
				return;
			}
		}

		if ($scope.teamId) {
			if (!$scope.userRoles.player && !$scope.userRoles.guardian && !$scope.userRoles.manager) {
				$scope.alerts.push({type: 'warning', msg: 'Du må velge minst én rolle på laget.'});
				return;
			}
		}

		var data = {
			'username' : $scope.username.toLowerCase(),
			'password' : $scope.password,
			'firstName': $scope.firstName,
			'lastName': $scope.lastName,
			'userRoles': $scope.userRoles,
			'newUser': $scope.newUser
		};

		if ($scope.teamName) {
			data.teamId = $scope.teamId;
		}

		$http.post(REST_API_URL + '/auth/register', data).success(function(data, status){

			if(!data.register){
				$scope.alerts.push({type: 'info', msg: 'Epost er allerede registrert.'});
			}

			userService.setName($scope.firstName + ' ' + $scope.lastName);
			mixpanel.track('New user successfully registered');
			$scope.firstLogin();

		}).error(function(data,status){
			mixpanel.track('New user registration error');
		});
	};

	$scope.firstLogin = function(){

		var username = $scope.username.toLowerCase();
		var password = $scope.password;

		var data = {'username' : username, 'password' : password};

		//remember to add new user to team!
		if ($scope.teamId) {
			data.teamId = $scope.teamId;
			data.userRoles = $scope.userRoles;
		}

		if(localStorage.getItem('gcmregid') !== null){
			data.gcm_regid = localStorage['gcmregid'];
		} else if (localStorage.getItem('iosToken') !== null) {
			data.ios_token = localStorage['iosToken']
		}

		userService.setNewUserRoles($scope.userRoles);

		$http({
			method: 'POST',
			data : data,
			url: REST_API_URL + '/auth/login',
			withCredentials: true,
		}).success(function(data){

			if(!data.login){
				if ($scope.teamId) {
					$scope.alerts = [{type: 'warning', msg: 'Brukeren er allerede registrert med et annet passord.'}];
					return;
				};
				$scope.alerts = [{type: 'warning', msg: 'Feil brukernavn eller passord.'}];
				return;
			}

			userService.setHasTeam(data.has_team);
			userService.setName(data.firstName + ' ' + data.lastName);
			userService.setAuth(true, data.auth_token);
			userService.setUserRoles(data.userRoles);
			userService.setUserName(username);
			userService.removeSignupUrl();

			if ($scope.teamId && $scope.userRoles.player) {
				$location.path('/register/newplayer/' + $scope.teamId);
				return;
			}

			if ($scope.teamId && $scope.userRoles.guardian) {
				$location.path('/register/guardian/addplayers/' + $scope.teamId);
				return;
			}

			if (!$scope.teamId) {
				$location.path('/get_started');
				return;
			}

			$location.path('/register/complete/' + $scope.teamId);

		}).error(function(data){
			$scope.alerts.push({type: 'warning', msg: data});
		});
	};


	$scope.redirectToLogin = function(){
		$location.path('/auth/login/');
	};


});
