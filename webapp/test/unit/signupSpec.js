/* global describe: true, expect: true, it: true, inject: true, module: true, beforeEach: true, afterEach: true */
'use strict';

describe('Signup', function () {
  beforeEach(module('sportsfronter'));

  describe('SignupController', function () {
    var signupController;

    beforeEach(inject(function ($controller, $rootScope, $httpBackend) {
      signupController = function () {
        return $controller('SignupController', {
          '$scope': $rootScope
        });
      };
      $httpBackend.expectGET('http://localhost:5000/auth/isauth').respond(200);
    }));

    afterEach(inject(function ($httpBackend) {
      $httpBackend.verifyNoOutstandingExpectation();
      $httpBackend.verifyNoOutstandingRequest();
    }));

    describe('when all is well it', function () {
      it('should not have any outstanding requests after initation of controller', inject(function ($httpBackend) {
        signupController();
        $httpBackend.flush();
      }));
    });

    describe('should always be true', function () {
      it('should always return true and be nice', inject(function ($httpBackend) {
        expect(true).toBe(true);
        $httpBackend.flush();
      }));
    });
  });
});
