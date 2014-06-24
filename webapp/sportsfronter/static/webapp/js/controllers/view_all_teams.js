var app = angular.module('sportsfronter');

app.controller('viewAllTeamsController', function($rootScope, $scope, $http, $location, $timeout, $routeParams) {

	$scope.teams = [];
	$scope.alerts = [];
	
	$scope.init = function() {
		$rootScope.init_navbar();
		fetchAllTeams();
	};


	var fetchAllTeams = function () {
		var url = REST_API_URL + '/management/allteams';
		$http({
			method: 'GET',
			url: url,
			withCredentials: true,
		}).success(function(data, status){
			if (data['logout']) {
				userService.logOut();
				$location.path( "/auth/login" );
			}

			$scope.coachTeams = data.coachTeams;
			$scope.guardianTeams = data.guardianTeams;
			$scope.playerTeams = data.playerTeams;

		}).error(function(data, status) {
			$scope.alerts.push({type: 'warning', comment: 'Det skjedde en feil ved henting av lag.'});
		});
	};


	$scope.goToTeamSearch = function() {
		$location.path('/team/search');
	};


	$scope.gotoViewTeams = function(teamId, teamName) {
		$location.path('team/' + teamId);
	};

	$scope.createNewTeam = function() {
		$location.path('/team/add');
	};

	var logout  = function(){
		$location.path( "/auth/login" );
	};

});
