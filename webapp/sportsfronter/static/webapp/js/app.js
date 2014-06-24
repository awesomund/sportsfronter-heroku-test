angular.module('sportsfronter',['ui.bootstrap','ngCookies', 'ngRoute'])

.config(['$httpProvider', function($httpProvider) {
        $httpProvider.defaults.useXDomain = true;
        delete $httpProvider.defaults.headers.common['X-Requested-With'];
    }
]).config(function($routeProvider,$httpProvider,$locationProvider,$compileProvider) {
	'use strict';
	$compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|ftp|mailto|maps|geo):/);
	$routeProvider
	.when('/', {
		templateUrl: '/static/webapp/html/all_events.html?v=0.61',
		controller: 'allEventsController',
		access: {
			isFree: false
		}
	})
	.when('/profile', {
		templateUrl: '/static/webapp/html/profile.html?v=0.61',
		controller: 'ProfileController',
		access: {
			isFree: false
		}
	})
	.when('/get_started', {
		templateUrl: '/static/webapp/html/get_started.html?v=0.61',
		controller: 'GetStartedController',
		access: {
			isFree: false
		}
	})
	.when('/signup', {
		templateUrl: '/static/webapp/html/signup.html?v=0.61',
		controller: 'SignupController',
		access: {
			isFree: true
		}
	})
	.when('/event/create', {
		templateUrl: '/static/webapp/html/create_event.html?v=0.61',
		controller: 'CreateEventController',
		access: {
			isFree: false
		}
	})
	.when('/event/edit/:eventId', {
		templateUrl: '/static/webapp/html/create_event.html?v=0.61',
		controller: 'CreateEventController',
		access: {
			isFree: false
		}
	})
	.when('/event/all', {
		templateUrl: '/static/webapp/html/all_events.html?v=0.61',
		controller: 'allEventsController',
		access: {
			isFree: false
		}
	})
	.when('/event/:eventId', {
		templateUrl: '/static/webapp/html/view_event.html?v=0.61',
		controller: 'ViewEventController',
		access: {
			isFree: false
		}
	})
	.when('/auth/login/', {
		templateUrl: '/static/webapp/html/login.html?v=0.61',
		controller: 'LoginController',
		access: {
			isFree: true
		}
	})
	.when('/team/add', {
		templateUrl: '/static/webapp/html/add_team.html?v=0.61',
		controller: 'AddTeamController',
		access: {
			isFree: false
		}
	})
	.when('/team/search', {
		templateUrl: '/static/webapp/html/team_search.html?v=0.61',
		controller: 'TeamSearchController',
		access: {
			isFree: false
		}
	})
	.when('/rsvp/:eventPlayerHash', {
		templateUrl: '/static/webapp/html/rsvp.html?v=0.61',
		controller: 'RsvpController',
		access: {
			isFree: true,
		}
	})
	.when('/team/all', {
		templateUrl: '/static/webapp/html/view_all_teams.html?v=0.61',
		controller: 'viewAllTeamsController',
		access: {
			isFree: false
		}
	})
	.when('/team/:teamId', {
		templateUrl: '/static/webapp/html/view_team.html?v=0.61',
		controller: 'viewTeamController',
		access: {
			isFree: false
		}
	})
	.when('/team/:teamId/nff', {
		templateUrl: '/static/webapp/html/nff.html?v=0.61',
		controller: 'viewTeamController',
		access: {
			isFree: false
		}
	})
	.when('/team/:teamId/player/add', {
		templateUrl: '/static/webapp/html/add_player.html?v=0.61',
		controller: 'AddPlayerController',
		access: {
			isFree: false
		}
	})
	.when('/team/:teamId/player/:playerId', {
		templateUrl: '/static/webapp/html/edit_player.html?v=0.61',
		controller: 'ManagementController',
		access: {
			isFree: false
		}
	})
	.when('/team/:teamId/coach/new', {
		templateUrl: '/static/webapp/html/add_coach.html?v=0.61',
		controller: 'ManagementController',
		access: {
			isFree: false
		}
	})
	.when('/team/:teamId/coach/:coachId', {
		templateUrl: '/static/webapp/html/add_coach.html?v=0.61',
		controller: 'ManagementController',
		access: {
			isFree: false
		}
	})
	.when('/invite/team/:teamId', {
		templateUrl: '/static/webapp/html/signup.html?v=0.61',
		controller: 'SignupController',
		access: {
			isFree: true
		}
	})
	.when('/register/guardian/addplayers/:teamId', {
		templateUrl: '/static/webapp/html/guardian_add_players.html?v=0.61',
		controller: 'GuardianAddPlayerController',
		access: {
			isFree: false
		}
	})
	.when('/register/newplayer/:teamId', {
		templateUrl: '/static/webapp/html/invite_link_new_player.html?v=0.61',
		controller: 'InviteLinkNewPlayerController',
		access: {
			isFree: false
		}
	})
	.when('/register/complete/:teamId', {
		templateUrl: '/static/webapp/html/invite_register_complete.html?v=0.61',
		controller: 'SignupController',
		access: {
			isFree: false
		}
	})
	.otherwise({redirectTo: '/auth/login',});


}).run( function($rootScope, $location, userService) {
	// TODO(8/2013) The userService call is likely needed only for logging purposes => verify, remove
	'use strict';
	userService.async().then(function() {
		
	});

	$rootScope.$on( '$routeChangeStart', function(event, next) {
		var nextAccessible = (next !== undefined) && (next.access !== undefined) && next.access.isFree === true;
		if (!userService.isAuth() && !nextAccessible) {
			$location.path( '/auth/login' );
		}
	});

}).directive('ngBlur', ['$parse', function($parse) {
	'use strict';
	return function(scope, element, attr) {
		var fn = $parse(attr.ngBlur);
		element.bind('blur', function(event) {
			scope.$apply(function() {
				fn(scope, {$event:event});
			});
		});
	};
}]).directive('ngEnter', function () {
	'use strict';
	return function (scope, element, attrs) {
		element.bind('keydown keypress', function (event) {
			if(event.which === 13) {
				scope.$apply(function (){
					scope.$eval(attrs.ngEnter);
				});
				event.preventDefault();
			}
		});
	};
});
