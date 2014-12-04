angular.module('ABToolExperiment', []).controller(
        'experimentController', function($scope, $window, $http) {
    // Use x-www-form-urlencoded Content-Type
    $http.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded;charset=utf-8";
    
    $scope.experiment = $window.modifiedExperiment;
    
    $scope.newTrackName = null;
    $scope.newTrackWeighting = null;
    
    $scope.addTrack = function() {
        // Don't add new track if newTrackName is empty
        if (!$scope.newTrackName) {
            return;
        }
        
        var i, len;
        // Don't add new track if name is the same as an existing track
        for (i = 0, len = $scope.experiment.tracks.length; i < len; i++) {
            if ($scope.experiment.tracks[i]["name"] == $scope.newTrackName) {
                $window.alert("There is already a track with that name");
                return;
            }
        }
        
        // Don't include value from hidden weight field if uniformRandom is true
        if ($scope.experiment.uniformRandom) {
            $scope.newTrackWeighting = null;
        }
        
        // Add the new track
        $scope.experiment.tracks.push({id: null, name: $scope.newTrackName,
            weighting: $scope.newTrackWeighting});
        $scope.newTrackName = null;
        $scope.newTrackWeighting = null;
    }
    
    $scope.uniformPercent = function() {
        return Math.round(100 / $scope.experiment.tracks.length);
    }
    
    $scope.submit = function() {
        // Payload has to be encoded using JQuery's $.param to submit properly
        var payload = $.param({"experiment": JSON.stringify($scope.experiment)});
        $http.post($window.submitURL, payload).
        success(function(data, status, headers, config) {
              $window.location = $window.parentPage;
          }).
          error(function(data, status, headers, config) {
              $window.alert("An error occured submitting this form")
          });
    }
    
    $scope.deleteTrack = function(track) {
        if (track["id"] != null) {
            if (! $window.confirm("Are you sure you want to delete track \"" + track["name"] +
                    "\"?  This will also delete any URLs associrated with that track.")) {
                return;
            }
            $http.post(track["deleteURL"]).
                error(function(data, status, headers, config) {
                    $scope.experiment.tracks.push(track)
                    $window.alert("An error occured deleting a track")
                });
        }
        var i, len;
        for (i = 0, len = $scope.experiment.tracks.length; i < len; i ++) {
            if ($scope.experiment.tracks[i] == track) {
                // Delete it from the experiment
                $scope.experiment.tracks.splice(i, 1);
            }
        }
    }
    
    $scope.difference = function() {
        var orig = $window.initialExperiment;
        var curr = $scope.experiment;
        if (orig.name != curr.name) { return true; }
        if (orig.notes != curr.notes) { return true; }
        if (orig.uniformRandom != curr.uniformRandom) { return true; }
        var origNumTracks = orig.tracks.length;
        var currNumTracks = curr.tracks.length;
        for (var j = 0; j < currNumTracks; j++) {
            for (var i = 0; i < origNumTracks; i++) {
                if (orig.tracks[i].id != curr.tracks[j].id) {
                    continue;
                }
                if (orig.tracks[i].name != curr.tracks[j].name) { return true; }
                if (orig.tracks[i].weighting != curr.tracks[j].weighting) { return true; }
                break;
            }
            if (i == origNumTracks) {
                // Loop reached end without hitting break statement,
                // meaning a track has been added
                return true;
            }
        }
        return false;
    }
    
    $scope.cancel = function() {
        var confirmCancel = $scope.difference();
        if (!confirmCancel) {
            $window.location = $window.parentPage;
        } else if ($window.confirm("You have unsaved changes. Are you sure you want to cancel?") == true) {
            $window.location = $window.parentPage;
        }
    }
    
});
