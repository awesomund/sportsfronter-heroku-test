var app = angular.module('sportsfronter');

app.controller('AddTeamController', function($scope, $http, $location, $rootScope, userService) {

	$scope.init = function() {
		$scope.teamName = "";
	}

	$scope.createTeam = function() {
		if (!$scope.teamName || $scope.teamName == "") {
			$scope.alerts = [{type: 'warning', msg: "Skriv inn lagnavn"}];
			return;
		}

		var data = {
			teamname: $scope.teamName,
		}

		$http({
			method: 'POST',
			url: REST_API_URL + '/management/team/add',
			withCredentials: true,
			data: data,
		}).success(function(data, status){

			userService.setHasTeam(true);
			$rootScope.userRoles.coach.push(data.team_id);
			$location.path('/team/' + data.team_id);

		}).error(function(data, status) {

			$scope.alerts = [{type: 'danger', msg: "Noe gikk galt. Prøv igjen"}];
			
		});
	}

	$scope.cancel = function() {
		$location.path('/team/all');
	}

	$scope.closeAlert = function(index) {
    	$scope.alerts.splice(index, 1);
  	}
	
});