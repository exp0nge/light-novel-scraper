/*jshint strict: true*/

var title = 'Light Novel Scrapper';

var app = angular.module('lightScrapApp', []);

// Custom interpolater
app.config(function($interpolateProvider){
  $interpolateProvider.startSymbol('//');
  $interpolateProvider.endSymbol('//');
});

app.factory('novelTasks', ['$http', function ($http) {
    'use strict';
    return {
        queue: function (novelInfo) {
            return $http.post('/task/', JSON.stringify(novelInfo));
        },
        status: function (taskId) {
            return $http.get('/task/' + taskId);
        },
        chapters: function (taskId) {
            return $http.get('/task/' + taskId + '/chapters/');
        }
    };
}]);

app.factory('epubTasks', ['$http', function ($http) {
    'use strict';
    return {
        queue: function (taskId) {
            return $http.post('/task/' + taskId + '/chapters/' + '/task/epub/', {});
        },
        status: function (taskId, epubTaskId) {
            return $http.get('/task/' + taskId + '/chapters/' + '/task/epub/' + epubTaskId);
        },
        download: function (taskId) {
            return $http.get('/task/' + taskId + '/chapters/' + '/d/epub/');
        }
    };
}]);


app.controller('HeadController', function (){
    'use strict';
    var vm = this;
    vm.title = title;
});


app.controller('MainController', ['tasks', function (tasks) {
    'use strict';
    var vm = this;
    vm.title = title;
    tasks.status('8ee278fb-bbb0-4e7b-82b3-84a625ffbbdf')
        .success(function(data){
            console.log(data);
        })
        .error(function(err){
            console.log(err);
        });
}]);
