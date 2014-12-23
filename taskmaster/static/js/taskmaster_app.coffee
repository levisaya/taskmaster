taskmasterApp = angular.module('taskmasterApp', ['ui.bootstrap', 'ui.router', 'ConsoleLogger'])

taskmasterApp.config(($locationProvider) ->
    $locationProvider.html5Mode(true);
)

taskmasterApp.run(['PrintToConsole', (PrintToConsole) ->
    PrintToConsole.active = true
])