// factory() allows one to define a service by returning
// an object that contains service functions and service
// data.  The service definition function is where one
// places the injectable services, such as $http and $q.
//

angular.module('myApp.services')
  .factory('User', function($http) {  // Injectables.
    var backendUrl = 'http://localhost:8000';
    var service = {
      user: {},
      setName: function(name) {
        service.user['name'] = name;
      },
      setEmail: function(email) {
        service.user['email'] = email;
      },
      save: function() {
        return $http.post(backendUrl + '/users', {
          user: service.user
        });
      }
   };
   return service;
 });

// To use a factory we inject it where it's needed
// at run-time.
//

angular.module('myApp')
  .controller('MainController', function($scope, User) {
    $scope.saveUser = User.save;
  });

// Factory is useful when one just needs to build
// a service with data and methods but nothing else
// particularly complex.

// Factory CANNOT be used to configure a service from
// the .config() section.




