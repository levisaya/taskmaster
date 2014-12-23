angular.module('taskmasterApp').controller('LogController',
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
            if $scope.canceller?
                $scope.canceller.resolve('')
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