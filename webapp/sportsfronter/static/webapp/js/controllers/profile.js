var app = angular.module('sportsfronter');

app.controller('ProfileController', function($rootScope,$scope, $location, $http, $timeout, $cookies, userService) {

	var setDays = function(){
		var dates = [];
		for (var i = 0; i < 31; i++){
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


	var now = new Date();
	setYears(now.getFullYear());
	setMonths();
	setDays();


	var setDateOfBirth = function(date){
		var tempDate = new Date(date);
		$scope.date = tempDate.getDate();
		$scope.month = tempDate.getMonth() + 1;
		$scope.year = parseInt(tempDate.getFullYear(), 10);
	};


	$scope.init = function(){
		$rootScope.init_navbar();
		getUserInfo();
		$scope.alerts = [];
	};

	var getUserInfo = function() {

		url = REST_API_URL + '/management/get_user_info';

		$http.get(url, {withCredentials : true
			}).success(function(data, status){

				if (data['logout']) {
					userService.logOut();
					$location.path( "/auth/login" );
				}

				$scope.userName = data.username;
				$scope.firstName = data.first_name;
				$scope.lastName = data.last_name;
				$scope.phoneNumber = data.phone_number;

				if (data.dateofbirth) {
					setDateOfBirth(data.dateofbirth);
				};

			}).error(function(data, status) {

			});
	};

	$scope.cancel = function() {
		$location.path('/');
	}
	
	$scope.updateUserInfo = function() {

		if (!$scope.userName || !$scope.firstName || !$scope.lastName) {
			$scope.alerts.push({type: 'warning', msg: "Brukernavn, fornavn og etternavn må være utfylt."});
			return;
		};

		if (!$scope.year || !$scope.month || !$scope.date) {
			var dateOfBirth = "";
		}
		else{
			var dateOfBirth = $scope.year + "-" + $scope.month + "-" + $scope.date;
		}

		var data = {
			'userName': $scope.userName,
			'firstName': $scope.firstName,
			'lastName': $scope.lastName,
			'phoneNumber': $scope.phoneNumber,
			'dateOfBirth': dateOfBirth,
		};

		$scope.alerts.push({type: 'info', comment: 'Oppdaterer... ', msg: ''})

		$http({
			method: 'POST',
			url: REST_API_URL + '/management/update_user_info',
			withCredentials: true,
			data: data,
		}).success(function(data, status){
			$scope.alerts.push({type: 'success', msg: "Dine oppdateringer er nå lagret"});
		}).error(function(data, status) {
			if (data['error']) {
				$scope.alerts.push({type: 'warning', msg: "Brukernavnet/eposten du prøvde å bytte til er opptatt."});
			}
			else{
				$scope.alerts.push({type: 'warning', msg: "Det har skjedd en feil."});
			}
		});

	};


	var getFormattedDate = function(){
		return $scope.year + "-" + $scope.month + "-" + $scope.date;
	};


	var daysInMonth = function(month, year) {
		return new Date(year, month, 0).getDate();
	};

	
});
