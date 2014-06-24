var app = angular.module('sportsfronter');

app.controller('viewTeamController', function($scope, $http, $location, $timeout, $routeParams, $rootScope) {

	'use strict';

	$scope.init = function() {
		$scope.teamName ='';
		$scope.teamId = '';
		$scope.players =[];
		$scope.coachs =[];
		$scope.predicate = 'shirt_number';
		$scope.direction = false;
		$scope.alerts = [];
		$scope.editTeamName = false;
		$scope.newTeamName = '';
		$scope.teamId = $routeParams.teamId;
		$scope.inviteLink = '';
		fetchTeam();
		$scope.coachName = $rootScope.name;
		determineUserPrivileges();
	};


	var determineUserPrivileges = function(){
		$scope.userIsCoach = false;
		
		for (var i = $rootScope.userRoles.coach.length - 1; i >= 0; i--) {
			if ($rootScope.userRoles.coach[i] == $scope.teamId) {
				$scope.userIsCoach = true;
			}
		}

		if ($scope.userIsCoach) {
			$scope.tableClass = 'table table-hover clickable';
		}
		else {
			$scope.tableClass = 'table';
		}

		
	};


	var fetchTeam  =  function(){
		var url = REST_API_URL + '/management/team/' + $routeParams.teamId;
		$http({
			method: 'GET',
			url: url,
			withCredentials: true,
		}).success(function(team, status) {
			if (team['logout']) {
				userService.logOut();
				$location.path( "/auth/login" );
				return;
			}

			$scope.teamName = team.name;
			$scope.players = team.players;
			$scope.coachs = team.coaches;
			$scope.inviteLink = REST_API_URL + '/#/invite/team/' + $scope.teamId + '?coach=' + $rootScope.name.replace(' ', '+');

			$scope.mailSubject = 'Påmelding til Sportsfronter';
			$scope.mailBody = 'For å gjøre det litt enklere å administrere laget, vil jeg heretter bruke Sportsfronter til å invitere til kamper og andre arrangementer. Det er enkelt for deg også.';
			$scope.mailBody += '%0A%0ARegistrer deg her (kopier og lim inn i din nettleser): ' + $scope.inviteLink;
			$scope.mailBody += '%0A%0ADu kan også laste ned en egen APP (iPhone/Android) for å selv få bedre oversikt over lagets aktiviteter.';
			$scope.mailBody += '%0A%0ALes mer om Sportsfronter her: www.sportsfronter.com';
			$scope.mailBody += '%0A%0AKontakt meg dersom du har spørsmål.';
			$scope.mailBody += '%0A%0AVennlig hilsen';
			$scope.mailBody += '%0A' + $scope.name;

		}).error(function(data, status) {

		});
	};


	$scope.sortTable = function(predicate){
		if($scope.predicate === predicate){
			$scope.direction = !$scope.direction;
		}
		
		else{
			$scope.predicate = predicate;
			$scope.direction = false;
		}
	};


	$scope.gotoPlayer = function(playerId) {
		if ($scope.userIsCoach) {
			$location.path('team/' + $scope.teamId + '/player/' + playerId);
		}
	};


	$scope.gotoCoach = function(id) {
		if (!$scope.userIsCoach) {
			return;
		}
		else if (id === 0){
			$location.path('team/' + $scope.teamId + '/coach/new');
		}
		else {
			$location.path('team/' + $scope.teamId + '/coach/' + id);
		}
	};


	$scope.createNewPlayer = function() {
		$location.path('team/'+$scope.teamId+'/player/add/');
	};


	$scope.addCoachsAsPlayer = function() {
		var data = {
			'team_id' : $scope.teamId,
		};

		$http({
			method: 'POST',
			url: REST_API_URL + '/management/addplayer',
			withCredentials: true,
			data: data,
		}).success(function(data, status) {
			if (data.status === 200) {
				$scope.alerts.push({type: 'success', msg: "Du er nå lagt til laget"});
				$scope.fetchPlayer();
			} else {
				$scope.alerts.push({type: 'danger', msg: "Du er spiller på laget"});
			}
		}).error(function(data, status) {
			$scope.alerts.push({type: 'danger', msg: "Noe gikk galt. Prøv igjen"});
		});
	};


	$scope.closeAlert = function(index) {
		$scope.alerts.splice(index, 1);
	};


	$scope.deleteTeam = function(){

		$http({

			method: 'POST',
			url: REST_API_URL + '/management/team/delete_team',
			withCredentials: true,
			data: {team_id: $scope.teamId, team_name: $scope.teamName},

		}).success(function(data, status) {

			$scope.alerts.push({type: 'success', msg: "Laget er slettet."});
			$timeout(redirectToTeams, 2000);


		}).error(function(data, status) {
			$scope.alerts.push({type: 'danger', msg: "Feil"});
		});
	};


	var redirectToTeams = function() {
	  $location.path("team/all");
	};


	$scope.changeTeamName = function(){
		$scope.editTeamName = false;

		$http({

			method: 'POST',
			url: REST_API_URL + '/management/team/change_team_name',
			withCredentials: true,
			data: {team_id: $scope.teamId, old_team_name: $scope.teamName, new_team_name: $scope.newTeamName},

		}).success(function(data, status) {

			$scope.teamName = data['new_team_name'];
			$scope.alerts.push({type: 'success', msg: "Navnet er endret."});
			$timeout(redirectToTeams, 2000);

		}).error(function(data, status) {
			$scope.alerts.push({type: 'danger', msg: "Feil"});
		});
	};


	$scope.goToNffPage = function() {
		$location.path('team/' + $scope.teamId + '/nff');
	};


	$scope.getICSViaBackend = function(){

		var data = {
				calendarURL: 'http://www.fotball.no/templates/portal/pages/GenerateICalendar.aspx?tournamentid=138918',
				nffUrl: $scope.nffUrl,
				teamId: $scope.teamId
			};

		$http({
			method: 'POST',
			url: REST_API_URL + '/management/team/getNFFiCalEvent',
			withCredentials: true,
			data: data
		}).success(function() {
			$scope.alerts.push({type: 'success', msg: 'Arrengement har blitt hentet! Sjekk arrangementsoversikten din.'});
		}).error(function() {
			$scope.alerts.push({type: 'warning', msg: 'Feil ved henting av arrangement.'});
		});
	};

});
