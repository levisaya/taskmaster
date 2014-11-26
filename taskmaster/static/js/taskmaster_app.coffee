taskmasterApp = angular.module('taskmasterApp', [])

taskmasterApp.controller('ProcessListController',
    ($scope, $http) ->
        $scope.process_list_model = {}
        $scope.last_status_time = 0.0

        $scope.update_model = (data) ->
            for process_index,model_data of data.process_data
                $scope.process_list_model[process_index] = model_data

            $scope.last_status_time = data.last_update_time

            $scope.reschedule_status_update()

        $scope.reschedule_status_update = () ->
            $http.get('process_status/' + $scope.last_status_time.toFixed(2)).
                success($scope.update_model).
                error($scope.reschedule_status_update)

        $scope.reschedule_status_update()
        return
    )
