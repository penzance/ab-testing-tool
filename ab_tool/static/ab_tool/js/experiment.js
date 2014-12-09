angular.module('ABToolExperiment', []).controller(
        'experimentController', function($scope, $window, $http) {
    // Use x-www-form-urlencoded Content-Type
    $http.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded;charset=utf-8";
    
    $scope.experiment = $window.modifiedExperiment;
    
    $scope.newTrackName = null;
    $scope.newTrackWeighting = null;
    
    $scope.addTrack = function() {
        /**
         * Add a new track based on the inputs in the new track form
         * (the fields in the new track form are bound to the variables
         * $scope.newTrackName and $scope.newTrackWeighting)
         */
        // Do nothing if newTrackName is empty
        if (!$scope.newTrackName) {
            return;
        }
        // Ignore newTrackWeighting if we are in uniformRandom mode
        if ($scope.experiment.uniformRandom) {
            $scope.newTrackWeighting = null;
        }
        
        $scope.experiment.tracks.push({id: null, name: $scope.newTrackName,
            weighting: $scope.newTrackWeighting});
        // Clear the new track form
        $scope.newTrackName = null;
        $scope.newTrackWeighting = null;
    };
    
    $scope.uniformPercent = function() {
        /**
         * Returns the percentage that should be displayed as weighting for
         * each track when uniformRandom is true.
         * Ex. if there are three tracks, this will return 33.
         */
        return Math.round(100 / $scope.experiment.tracks.length);
    }
    
    $scope.submit = function() {
        /**
         * Submits form contents to the backend and redirects to window.parentPage
         */
        // Payload has to be encoded using JQuery's $.param to submit properly
        var payload = $.param({"experiment": JSON.stringify($scope.experiment)});
        $http.post($window.submitURL, payload).
        success(function(data, status, headers, config) {
            $window.location = $window.parentPage;
          }).
          error(function(data, status, headers, config) {
            // TODO: add error behavior
          });
    }
    
    $scope.difference = function() {
        /**
         * Returns true iff the experiment currently in the form differs from
         * the one the form started with, so that a confirmation can be
         * selectively displayed on cancelChanges.  Note that deleted tracks
         * are not included in the difference because track deletion is
         * confirmed separately.
         */
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
        /**
         * Navigates to parent page without saving changes on backend;
         * confirms cancelation if changes have been made (as determined by
         * the difference function).
         */
        var message = "You have unsaved changes. Are you sure you want to cancel?";
        var confirmCancel = $scope.difference();
        if (!confirmCancel || confirm(message)) {
            $window.location = $window.parentPage;
        }
    };
    
});
