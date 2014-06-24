var app = angular.module('sportsfronter');

app.controller('TeamSearchController', function($rootScope, $scope, $http, $location, userService) {

	'use strict';

	$scope.searchResultTeams = [];
	$scope.alerts = [];
	$scope.searchFinished = false;
	$scope.showJoinTeamOptions = false;
	$scope.joinTeamRoles = {
		player: false,
		guardian: false,
		manager: false
	};
	$rootScope.joinTeamRoles = $scope.joinTeamRoles;


	var fetchTeam  =  function(){
		var url = REST_API_URL + '/management/team/' + $scope.selectedTeam.id;
		$http({
			method: 'GET',
			url: url,
			withCredentials: true,
		}).success(function(team) {
			if (team.logout) {
				userService.logOut();
				$location.path( '/auth/login');
				return;
			}

			$scope.viewTeam(team);
		});
	};

	
	$scope.init = function() {
		$rootScope.init_navbar();
	};


	$scope.search = function(){
		$scope.selectedTeam = undefined;
		$scope.searchResultTeams = [];
		$scope.alerts = [];

		$http.get(REST_API_URL + '/management/team/search/' + $scope.searchTerm)
		.success(function(data){
			$scope.searchResultTeams = data.results;
		});

		$scope.searchFinished = true;
	};


	$scope.viewTeam = function(team){
		$scope.selectedTeam = team;
		$scope.searchResultTeams = [];
	};


	$scope.joinTeam = function(){

		if (!$scope.joinTeamRoles.player && !$scope.joinTeamRoles.guardian && !$scope.joinTeamRoles.manager) {
			$scope.alerts.push({type: 'warning', msg: 'Du må velge minst én rolle på laget.'});
			return;
		}

		userService.setNewUserRoles($scope.joinTeamRoles);
		$rootScope.joinTeamRoles = userService.getNewUserRoles();

		if ($scope.joinTeamRoles.manager || $scope.joinTeamRoles.player) {

			var data = $scope.joinTeamRoles;

			$http({
				method: 'POST',
				url: REST_API_URL + '/management/team/' + $scope.selectedTeam.id + '/join',
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

		if ($scope.joinTeamRoles.player) {
			$location.path('/register/newplayer/' + $scope.selectedTeam.id);
			return;
		}

		if ($scope.joinTeamRoles.guardian) {
			$location.path('/register/guardian/addplayers/' + $scope.selectedTeam.id);
			return;
		}

	};


	$scope.abortJoinTeam = function() {
		$scope.joinTeamRoles = {
			player: false,
			guardian: false,
			manager: false
		};
		$scope.showJoinTeamOptions = false;
	};


	$scope.gotoViewTeams = function(teamId) {
		$location.path('team/' + teamId);
	};


	$scope.createNewTeam = function() {
		$location.path('/team/add');
	};


});
