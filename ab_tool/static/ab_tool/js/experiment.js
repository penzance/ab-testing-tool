angular.module('ABToolExperiment', ['ABToolExperiment.controllers']);
angular.module('ABToolExperiment', []).controller('experimentController', function($scope, $window) {
    $scope.experiment = $window.modifiedExperiment;
    
    $scope.newTrackName = null;
    $scope.newTrackWeighting = null;
    
    $scope.addTrack = function() {
        if (!$scope.newTrackName) {
            return;
        }
        $scope.experiment.tracks.push({id: null, name: $scope.newTrackName,
            weighting: $scope.newTrackWeighting});
        $scope.newTrackName = null;
        $scope.newTrackWeighting = null;
    };
    
    $scope.difference = function() {
        var orig = $window.initialExperiment;
        var curr = $scope.experiment;
        if (orig.name != curr.name) { return true; }
        if (orig.notes != curr.notes) { return true; }
        if (orig.uniformRandom != curr.uniformRandom) { return true; }
        var origNumTracks = orig.tracks.length;
        var currNumTracks = curr.tracks.length;
        if (origNumTracks != currNumTracks) { return true; }
        for (var i = 0; i < origNumTracks; i++) {
            for (var j = 0; j < currNumTracks; j++) {
                if (orig.tracks[i].id != curr.tracks[j].id) {
                    continue;
                }
                if (orig.tracks[i].name != curr.tracks[j].name) { return true; }
                if (orig.tracks[i].weighting != curr.tracks[j].weighting) { return true; }
            }
        }
        return false;
    }
    
    $scope.cancel = function() {
        var confirmCancel = $scope.difference();
        return $window.cancelChanges(confirmCancel);
    };
    
});
