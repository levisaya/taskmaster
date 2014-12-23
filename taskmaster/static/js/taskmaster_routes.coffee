index =
    name: 'index'
    url: '/'
    views:
        body:
            templateUrl: 'static/templates/index/main_page_body.html'
        includes:
            templateUrl: 'static/templates/index/main_page_includes.html'

processDetails =
    name: 'processDetails'
    url: '/process-details/{process_index:int}'
    templateUrl: '/'
    views:
        body:
            template: '<div>Process</div>'
        includes:
            templateUrl: 'static/templates/index/main_page_includes.html'

angular.module('taskmasterApp').config(($stateProvider, $urlRouterProvider) ->
    $urlRouterProvider.otherwise('/');

    $stateProvider
        .state(index)
        .state(processDetails)
)