var app = angular.module('sportsfronter');
app.factory('userService', function($http, $q, $cookies,$cookieStore, $rootScope) {
  var deffered = $q.defer();
  var data = [];  
  var userService = {};
  var isAuth;

  userService.isAuth = function(){
    if (localStorage['is_auth'] === "true"){
    //if ($cookies.sessionid || localStorage['is_auth'] === "true"){
      return true;      
    }
    else {
      return false;
    }
    //return $cookies.sessionid != undefined;
  }
  
  userService.init  = function(){
    $http.defaults.headers.common['Authorization'] = localStorage['auth_token']
  }

  userService.setAuth = function(value, token){
     isAuth = value;
     localStorage['is_auth'] = "true";
     $http.defaults.headers.common['Authorization'] = token;
     localStorage['auth_token'] = token;
  }

  userService.logOut = function(){
    $cookieStore.remove("sessionid");
    localStorage['auth_token'] = "";
    localStorage['is_auth'] = "false";
    isAuth = false;
  }

  userService.name   = function(){
    return name;
  }

  userService.setName = function(name) {
    localStorage['name'] = name;
  }

  userService.getName = function(){
    if (localStorage['name'] === undefined){
      return '';
    }
    else {
      return localStorage['name'];
    }
  }

  userService.async = function() {
    $http({
       method: 'GET',
       url: REST_API_URL + '/auth/isauth',
       withCredentials: true,
       }).success(function(d){
          data = d;
          //is_authz = d.is_auth;
          //name = d.name;
          //siteHasLoaded = true;
          deffered.resolve(d);

     });
    return deffered.promise;
  };

  userService.isIos = function(){
    return localStorage['iosToken'] !== undefined;
  }

  userService.isAndroid = function(){
    return localStorage['gcmregid'] !== undefined;
  }

  userService.data = function() { return data; };

  userService.hasTeam = function() {
    if (localStorage['hasTeam'] === undefined){
        return false;
      }
      else return localStorage['hasTeam'] == "true";
  };

  userService.setHasTeam = function(value) {
    localStorage['hasTeam'] = value;
  };

  userService.setUserRoles = function(userRoles) {
    localStorage.setItem('userRoles', JSON.stringify(userRoles));
  };

  userService.getUserRoles = function() {
    if (localStorage.userRoles) {
      return JSON.parse(localStorage.userRoles);
    }
  };

  userService.setNewUserRoles = function(newUserRoles) {
    localStorage.setItem('newUserRoles', JSON.stringify(newUserRoles));
  };

  userService.getNewUserRoles = function() {
    if (localStorage.newUserRoles) {
      return JSON.parse(localStorage.newUserRoles);
    }
  };

  userService.determineUserPrivileges = function(){
    //determines GENERAL user privileges. Not privileges relative to a certain team.
    
    var url = REST_API_URL + '/auth/get_user_roles';

    $http({
      method: 'GET',
      url: url,
      withCredentials: true,
    }).success(function(data) {

      $rootScope.userRoles = data;

      var privileges = {
        coach: false,
        guardian: false,
        player: false
      };

      if (data.coach.length) {
        privileges.coach = true;
      }
      if (data.guardian.length) {
        privileges.guardian = true;
      }
      if (data.player.length) {
        privileges.player = true;
      }

      $rootScope.userPrivileges = privileges;
      userService.setUserPrivileges(privileges);

      return privileges;

    });
  };

  userService.setUserPrivileges = function(userPrivilegesObject){
    localStorage.setItem('userPrivileges', JSON.stringify(userPrivilegesObject));
  };

  userService.getUserPrivileges = function() {
    if (localStorage.userPrivileges) {
      return JSON.parse(localStorage.userPrivileges);
    }
  };

  userService.setUserName = function(userName) {
    localStorage.setItem('userName', userName);
  };

  userService.getUserName = function() {
    if (localStorage.userName) {
      return localStorage.userName;
    }
  };

  userService.setSignupUrl = function(signupUrl) {
    localStorage.setItem('signupUrl', signupUrl);
  };

  userService.getSignupUrl = function() {
    if (localStorage.getItem('signupUrl')) {
      return localStorage.signupUrl;
    }
  };

  userService.removeSignupUrl = function() {
    if (localStorage.getItem('signupUrl')) {
      localStorage.removeItem('signupUrl');
    }
  };

  return userService;
});