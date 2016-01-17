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
        queue: function (novelInfo, toc_bool) {
            if (toc_bool) {
                return $http.post('/task/toc/', JSON.stringify({'title': novelInfo.title,
                                                                'start': novelInfo.start,
                                                                'end': novelInfo.end,
                                                                'url': novelInfo.urlTOC }));
            }
            return $http.post('/task/', JSON.stringify({'title': novelInfo.title,
                                                                'start': novelInfo.start,
                                                                'end': novelInfo.end,
                                                                'url': novelInfo.url }));
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
            return $http.post('/task/' + taskId + '/chapters/task/epub/', {});
        },
        status: function (taskId, epubTaskId) {
            return $http.get('/task/' + taskId + '/chapters/task/epub/' + epubTaskId);
        },
        download: function (taskId, title) {
            window.location = '/task/' + taskId + '/chapters/d/epub/?title=' + title;
        }
    };
}]);


app.controller('HeadController', function () {
    'use strict';
    var vm = this;
    vm.title = title;
});


app.controller('MainController', ['$interval', '$http', 'novelTasks', 'epubTasks', function ($interval, $http, novelTasks, epubTasks) {
    'use strict';
    var vm = this;
    vm.title = title;
    vm.verbose = null;
    vm.htmlReady = false;
    vm.epubReady = false;
    vm.zipDownloadLink = null;
    vm.taskId = null;
    vm.celeryStatus = false;
    vm.progressBar = 0;
    vm.scrapForm = {
        'title': 'smartphone',
        'start': 31,
        'end': 33,
        'url': 'http://raisingthedead.ninja/2015/10/06/smartphone-chapter-31/',
        'urlTOC': 'http://raisingthedead.ninja/current-projects/in-a-different-world-with-a-smartphone/'
    };
    vm.current_chapter = vm.scrapForm.start;
    $http.get('/ping')
        .success(function (res) {
            if (res != 'null'){
              vm.celeryStatus = true;
            }
        });
    vm.submitScrapRequest = function (toc_bool) {
        vm.hideSubmit = true;
        vm.htmlReady = false;
        novelTasks.queue(vm.scrapForm, toc_bool)
            .success(function (res) {
                var novelStatusChecker;
                if (res.status === 'success') {
                    vm.verbose = 'Checking...';
                    var progressTotal = (parseInt(vm.scrapForm.end) - parseInt(vm.scrapForm.start)) + 1;
                    var progressDiff = 0;
                    var prevChapter = parseInt(vm.scrapForm.start) - 1;
                    vm.progressBar = progressDiff / progressTotal;
                    novelStatusChecker = $interval(function () {
                        console.log('checking');
                        vm.taskId = res.taskId;
                        novelTasks.status(vm.taskId)
                            .success(function (statusRes) {
                                vm.verbose = statusRes.state;
                                if (statusRes.state === 'SUCCESS') {
                                    vm.progressBar = 100;
                                    vm.current_chapter = vm.scrapForm.end;
                                    vm.hideSubmit = false;
                                    $interval.cancel(novelStatusChecker);
                                    vm.htmlReady = true;
                                    vm.zipDownloadLink = '/task/' + vm.taskId + '/chapters/d/zip/';
                                }
                                else if (statusRes.state === 'PROGRESS') {

                                    vm.current_chapter = statusRes.info.current_chapter;
                                    if (parseInt(vm.current_chapter) > prevChapter){
                                        progressDiff++;
                                        vm.progressBar = progressDiff / progressTotal * 100;
                                        prevChapter++;
                                        console.log(vm.progressBar);
                                    }

                                    console.log(vm.progressBar);
                                }
                            })
                            .error(function (statusErr) {
                                console.log(statusErr);
                                vm.verbose = 'ERROR OCCURRED';
                                vm.hideSubmit = false;
                                $interval.cancel(novelStatusChecker);
                            });
                    }, 1000);
                }

            })
            .error(function (err) {
                console.log(err);
                vm.verbose = 'ERROR OCCURRED';
            });
    };
    vm.submitePubRequest = function () {
        epubTasks.queue(vm.taskId)
            .success(function (res) {
                vm.epubReady = true;
                var epubStatusChecker;
                console.log(res);
                vm.verbose = res.state;
                epubStatusChecker = $interval(function () {
                    console.log('checking epub status');
                    epubTasks.status(vm.taskId, res.epubTaskId)
                        .success(function (statusRes) {
                            vm.epubResults = statusRes;
                            if (statusRes.state === 'SUCCESS') {
                                $interval.cancel(epubStatusChecker);
                                console.log('grabbing %s', vm.taskId);
                                epubTasks.download(vm.taskId, vm.scrapForm.title);
                                vm.epubReady = false;
                                vm.verbose = 'SUCCESS';
                            }
                        })
                        .error(function (err) {
                            console.log(err);
                            vm.verbose = 'ERROR OCCURRED';
                            vm.hideSubmit = false;
                            $interval.cancel(epubStatusChecker);
                        });
                }, 1000);
            })
            .error(function (err) {
                console.log(err);
                vm.verbose = 'ERROR OCCURRED';
            });
    };


}]);
