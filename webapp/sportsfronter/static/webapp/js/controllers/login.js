var app = angular.module('sportsfronter');

app.controller('LoginController', function($rootScope,$scope, $http, $location,$window, userService){

	var firstTimeLogin = false;

	$scope.init = function(){
		$rootScope.init_navbar();
		mixpanel.track("User viewed login page");

		$scope.signupUrl = userService.getSignupUrl();
		if ($scope.signupUrl) {
			$scope.showInviteLinkDialog = true;
		}
	};

	$scope.useInviteLink = function(){
		$window.location.href = $scope.signupUrl;
	};


	$scope.forgotPasswordURL = REST_API_URL + "/admin/password_reset/";

	$scope.enterLogin = function(event){
		if (event.which == 13) {
			$scope.login();
		}
	};


	$scope.login = function(){

		if (!$scope.username) {
			$scope.alerts = [{type: 'warning', msg: "Du må fylle inn et gyldig brukernavn."}];
			return;
		}

		if (!$scope.password) {
			$scope.alerts = [{type: 'warning', msg: "Du må fylle inn passord."}];
			return;
		}

		var username = $scope.username.toLowerCase();
		var password = $scope.password;

		if(localStorage.getItem('gcmregid') !== null){
			data = {'username' : username, 'password' : password, 'gcm_regid' : localStorage['gcmregid']};
		} else if (localStorage.getItem('iosToken') != null) {
			data = {'username' : username, 'password' : password, 'ios_token' : localStorage['iosToken']};
		}
		else{
			data = {'username' : username, 'password' : password};
		}

		$http({
			method: 'POST',
			data : data,
			url: REST_API_URL + '/auth/login',
			withCredentials: true,
		}).success(function(data, status){
			if(!data.login){
				$scope.alerts = [{type: 'warning', msg: "Feil brukernavn eller passord"}];
				return;
			}

			userService.setHasTeam(data.has_team);
			userService.setName(data.firstName + ' ' + data.lastName);
			userService.setAuth(true, data.auth_token);
			userService.setUserRoles(data.userRoles);
			userService.setUserName(username);
			userService.removeSignupUrl();

			if(firstTimeLogin){
				firstTimeLogin = false;
				$location.path("/team/all");
			} else{
				$location.path("/");
			}
		}).error(function(data, status) {
			$scope.alerts = [{type: 'warning', msg: data}];
		});
	};


	$scope.closeAlert = function(index){
			$scope.alerts.splice(index, 1);
	};


	$scope.redirectToSignup = function(){
				$location.path( "/signup/" );
	};


});