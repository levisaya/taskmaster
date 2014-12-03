taskmasterApp = angular.module('taskmasterApp', ['ui.bootstrap'])

taskmasterApp.controller('ProcessListController',
    ($scope, $http, $timeout) ->
        $scope.process_list_model = {}
        $scope.last_status_time = 0.0
        $scope.last_log_time = 0.0

        $scope.log_process_index = null
        $scope.log_buffer = []

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

        $scope.recv_logs = (data) ->
            if data.process_index = $scope.log_process_index
                Array::push.apply($scope.log_buffer, data.output)
                $scope.last_log_time = data.last_output_time

                $scope.subscribe_to_logs(data.process_index)

        $scope.subscribe_unsubscribe_to_logs = (process_index) ->
            if process_index == $scope.log_process_index
                #Unsubscribe
                $scope.log_process_index = null
                $scope.log_buffer = []
                $scope.last_log_time = 0.0
            else
                $scope.subscribe_to_logs(process_index)

        $scope.subscribe_to_logs = (process_index, delay = 0) ->
            if process_index != $scope.log_process_index
                $scope.log_buffer = []
                $scope.last_log_time = 0.0
                $scope.log_process_index = process_index

            http_get = () -> $http.get('logs/streaming/' + process_index + '/0/' + $scope.last_log_time.toFixed(2)).
                                       success($scope.recv_logs).
                                       error(-> $scope.subscribe_to_logs(process_index, 1000))
            $timeout(http_get, delay)

        $scope.reschedule_status_update()
        return
    )
