/*jshint strict: true*/

var title = 'Light Novel Scrapper';

var app = angular.module('lightScrapApp', []);

app.config(function ($interpolateProvider) {
    'use strict';
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


app.controller('HeadController', function () {
    'use strict';
    var vm = this;
    vm.title = title;
});


app.controller('MainController', ['novelTasks', '$interval', function (novelTasks, $interval) {
    'use strict';
    var vm = this;
    vm.title = title;
    vm.results = null;
    vm.scrapForm = {
        'title': 'smartphone',
        'start': 31,
        'end': 33,
        'url': 'http://raisingthedead.ninja/2015/10/06/smartphone-chapter-31/'
    };
    vm.submitScrapRequest = function () {
        novelTasks.queue({
            'title': vm.scrapForm.title,
            'start': vm.scrapForm.start,
            'end': vm.scrapForm.end,
            'url': vm.scrapForm.url
        })
            .success(function (res) {
                var novelStatusChecker;
                if (res.status === 'success') {
                    vm.results = 'Checking status';
                    novelStatusChecker = $interval(function () {
                        console.log('checking');
                        novelTasks.status(res.taskId)
                            .success(function (statusRes) {
                                vm.results = statusRes;
                                if (statusRes.state === 'SUCCESS') {
                                    $interval.cancel(novelStatusChecker);
                                }
                            })
                            .error(function (statusErr) {
                                console.log(statusErr);
                            });
                    }, 1000);
                }

            })
            .error(function (err) {
                console.log(err);
            });
    };

    novelTasks.status('8ee278fb-bbb0-4e7b-82b3-84a625ffbbdf')
        .success(function (data) {
            console.log(data);
        })
        .error(function (err) {
            console.log(err);
        });

}]);
