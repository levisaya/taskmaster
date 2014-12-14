taskmasterApp = angular.module('taskmasterApp', ['ui.bootstrap'])

taskmasterApp.controller('LogController',
    ($scope, $http, $timeout, $q) ->
        $scope.last_log_time = 0.0
        $scope.last_time_index = 0
        $scope.log_buffer = []

        $scope.subscribed = false
        $scope.canceller = null

        $scope.recv_logs = (data) ->
            Array::push.apply($scope.log_buffer, data.output)
            $scope.last_log_time = data.last_output_time
            $scope.last_time_index = data.time_index
            if $scope.subscribed
                $scope.subscribe_to_logs()

        $scope.unsubscribe_to_logs = () ->
            $scope.canceller.resolve('derp')
            $scope.log_buffer = []
            $scope.last_log_time = 0.0
            $scope.last_time_index = 0

        $scope.$on("$destroy", $scope.unsubscribe_to_logs)

        $scope.subscribe_to_logs = (delay = 0) ->
            $scope.canceller = $q.defer()
            http_get = () -> $http.get('logs/streaming/' + $scope.$parent.$index + '/' + $scope.last_log_time.toFixed(2) + '/' + $scope.last_time_index,
                                       {timeout: $scope.canceller.promise}).
                                       success($scope.recv_logs).
                                       error(-> if $scope.subscribed
                                                       subscribe_to_logs(1000))
            $timeout(http_get, delay)

        $scope.stop_start = (event, process_index) ->
            if process_index == $scope.$parent.$index and $scope.subscribed == false
                $scope.subscribed = true
                $scope.subscribe_to_logs()
            else if $scope.subscribed
                $scope.subscribed = false
                $scope.unsubscribe_to_logs()

        $scope.$on('selected_process', $scope.stop_start)

        return
    )

taskmasterApp.controller('ProcessListController',
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
