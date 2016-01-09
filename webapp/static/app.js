var title = 'Light Novel Scrapper';

var app = angular.module('lightScrapApp', []);

// Custom interpolater
app.config(function($interpolateProvider){
  $interpolateProvider.startSymbol('//');
  $interpolateProvider.endSymbol('//');
});

app.controller('HeadController', function(){
  var vm = this;
  vm.title = title;
})


app.controller('MainController', function() {
  var vm = this;
  vm.title = title;
});
