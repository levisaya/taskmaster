// Generated by CoffeeScript 1.8.0
(function() {
  angular.module('taskmasterApp').controller('ProcessListController', function($scope, $http, $timeout) {
    $scope.process_list_model = {};
    $scope.last_status_time = 0.0;
    $scope.previously_selected = null;
    $scope.update_model_with_status = function(data) {
      var model_data, process_index, _ref;
      _ref = data.process_data;
      for (process_index in _ref) {
        model_data = _ref[process_index];
        if (!(process_index in $scope.process_list_model)) {
          $scope.process_list_model[process_index] = {};
          $http.get('process_info/' + process_index).success(function(info_data) {
            return $scope.process_list_model[info_data.index].info = info_data;
          });
        }
        $scope.process_list_model[process_index].status = model_data;
        console.log($scope.process_list_model[process_index]);
      }
      $scope.last_status_time = data.last_update_time;
      return $scope.reschedule_status_update();
    };
    $scope.reschedule_status_update = function(delay) {
      var http_get;
      if (delay == null) {
        delay = 0;
      }
      http_get = function() {
        return $http.get('process_status/' + $scope.last_status_time.toFixed(2)).success($scope.update_model_with_status).error(function() {
          return $scope.reschedule_status_update(1000);
        });
      };
      $timeout(http_get, delay);
    };
    $scope.start_process = function(process_index) {
      return $http.post('process/' + process_index + '/start');
    };
    $scope.stop_process = function(process_index) {
      return $http.post('process/' + process_index + '/kill');
    };
    $scope.set_open_process = function(process_index) {
      if ($scope.previously_selected === process_index) {
        $scope.previously_selected = null;
      } else {
        $scope.previously_selected = process_index;
      }
      return $scope.$broadcast('selected_process', $scope.previously_selected);
    };
    $scope.reschedule_status_update();
  });

}).call(this);