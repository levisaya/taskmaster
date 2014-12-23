angular.module('taskmasterApp').controller('ProcessListController',
    ($scope, $http, $timeout) ->
        $scope.process_list_model = {}
        $scope.last_status_time = 0.0

        $scope.previously_selected = null

        $scope.update_model_with_status = (data) ->
            for process_index,model_data of data.process_data
                if process_index not of $scope.process_list_model
                    $scope.process_list_model[process_index] = {}
                    $http.get('process_info/' + process_index).
                          success((info_data)-> $scope.process_list_model[info_data.index].info = info_data)
                $scope.process_list_model[process_index].status = model_data
                console.log($scope.process_list_model[process_index])

            $scope.last_status_time = data.last_update_time

            $scope.reschedule_status_update()

        $scope.reschedule_status_update = (delay = 0) ->
            http_get = () -> $http.get('process_status/' + $scope.last_status_time.toFixed(2)).
                                    success($scope.update_model_with_status).
                                    error(-> $scope.reschedule_status_update(1000))
            $timeout(http_get, delay)
            return

        $scope.start_process = (process_index) ->
            $http.post('process/' + process_index + '/start')

        $scope.stop_process = (process_index) ->
            $http.post('process/' + process_index + '/kill')

        $scope.set_open_process = (process_index) ->
            if $scope.previously_selected == process_index
                $scope.previously_selected = null
            else
                $scope.previously_selected = process_index

            $scope.$broadcast('selected_process', $scope.previously_selected)

        $scope.reschedule_status_update()
        return
    )