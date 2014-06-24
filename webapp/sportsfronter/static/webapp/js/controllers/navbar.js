var app = angular.module('sportsfronter');

app.controller('NavbarController', function($rootScope, $scope, $http, $location, userService) {

  $scope.alerts = [];
  $scope.isAuth = false;

  $scope.init = function() {
    $scope.show_logout = showLogoutButton();
    $scope.show_login = showLoginButton();
    $scope.show_signup = showSignupButton();
    $rootScope.name = userService.getName();
    $rootScope.userRoles = userService.getUserRoles();
    $rootScope.userName = userService.getUserName();
    $rootScope.userPrivileges = userService.determineUserPrivileges();
  };

  $rootScope.init_navbar = function(){
    $scope.init();
  }

  var showLogoutButton = function(){
    return userService.isAuth();
  }
  var showLoginButton = function(){
    return $location.path() == "/signup";
  }

  var showSignupButton = function(){
    return $location.path() == "/auth/login/";
  }

  $scope.login =  function(){
      $location.path( "/auth/login/" );
  }
  $scope.signup =  function(){
      $location.path( "/signup" );
  }  

  $scope.logout  = function(){
    $http({
       method: 'GET',
       url: REST_API_URL + '/auth/logout',
       withCredentials: true,
       }).success(function(d){
          userService.logOut();
          $location.path( "/auth/login" );
     });
  }

  $scope.back  = function(){
    window.history.back();
  }


  $scope.show_logout = showLogoutButton();
  $scope.show_login = showLoginButton();
  $scope.show_signup = showSignupButton();
  $rootScope.name = userService.getName();
  $rootScope.userRoles = userService.getUserRoles();
  $rootScope.userName = userService.getUserName();
  $rootScope.userPrivileges = userService.determineUserPrivileges();

});


