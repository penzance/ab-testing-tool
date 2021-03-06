var controller = function($scope, $window, $http) {
    /**
     * Angular controller (attached to angular module at bottom of file)
     */
    
    // Use x-www-form-urlencoded Content-Type
    $http.defaults.headers.post["Content-Type"] = "application/x-www-form-urlencoded;charset=utf-8";
    
    $scope.experiment = $window.modifiedExperiment;
    $scope.submitting = false;
    
    $scope.newTrackName = null;
    $scope.newTrackWeighting = null;
    
    $scope.nameError = null;
    $scope.weightingError = null;
    
    $scope.addTrack = function() {
        /**
         * Add a new track based on the inputs in the new track form
         * (the fields in the new track form are bound to the variables
         * $scope.newTrackName and $scope.newTrackWeighting)
         */
        // Don't include value from hidden weight field if uniformRandom or
        // csvUplaod is true
        if ($scope.experiment.uniformRandom || $scope.experiment.csvUpload) {
            $scope.newTrackWeighting = null;
        }
        var newTrack = {id: null, name: $scope.newTrackName, editing: false,
                weighting: $scope.newTrackWeighting, newName: $scope.newTrackName};
        
        // Do nothing if newTrackName is empty or conflicts
        if (!$scope.newTrackName || !$scope.isTrackOK(newTrack)) {
            return;
        }
        
        // Add the new track
        $scope.experiment.tracks.push(newTrack);
        // Clear the new track form
        $scope.newTrackName = null;
        $scope.newTrackWeighting = null;
    }
    
    $scope.uniformPercent = function() {
        /**
         * Returns the percentage that should be displayed as weighting for
         * each track when uniformRandom is true.
         * Ex. if there are three tracks, this will return 33.
         */
        return Math.round(100 / $scope.experiment.tracks.length);
    }
    
    $scope.percentsTotal100 = function() {
        /**
         * Returns a boolean as to whether or not the tracks add up to 100.
         * If the return is false, raises an alert.
         */
        //set a resuable len
        var len = $scope.experiment.tracks.length;
        
        if ($scope.experiment.uniformRandom || $scope.experiment.csvUpload) {
            // If uniformRandom is true, the actual track weights are ignored.
            // If csvUpload is true, there are no track weights.
            return true;
        }
        
        for (var i = 0, sum = 0; i < len; i++) {
            
            var weighting = $scope.experiment.tracks[i].weighting;
            if (weighting) {
                sum += parseInt(weighting);
            } else {
                $scope.experiment.tracks[i].weighting = 0
            }
        }
        if (sum != 100) {
            // TODO: replace with better error display
            //add an error class to every input field with the track fieldset
            //$('.input-group-right').addClass('has-error');
            //alert("Your track weightings add up to " + sum + "%.  This needs to be 100%.");
            $scope.weightingError = "The weights need to add up to 100%.  "
                + "They currently add up to " + sum + "%.";
        }else{
            $scope.weightingError = null;
        }
        
        return (sum == 100);
    }
    
    $scope.showConfirmation = function() {
        /**
         * If the form validates, display the confirmation modal to the user
         */
        
        if ($scope.experiment.name == ''){
            $scope.nameError = true;
            return false;
        }
        
        $scope.nameError = false;
        
        if ($scope.percentsTotal100()) {
            $("#confirmSubmit").modal('show');
        }
    }
    
    $scope.submit = function() {
        /**
         * Submits form contents to the backend and redirects to window.parentPage
         */
        // Payload has to be encoded using JQuery's $.param to submit properly
        //var payload = $.param({"experiment": JSON.stringify($scope.experiment)});
        $scope.submitting = true;
        $http.post($window.submitURL, $scope.experiment).
          success(function(data, status, headers, config) {
              $window.location = $window.parentPage;
          }).
          error(function(data, status, headers, config) {
              $scope.submitting = false;
              $window.alert("Sorry, an error occurred when submitting the form. Please make sure that the experiment name is unique and under 250 characters and that notes are less than 8000 characters.")
          });
    }
    
    $scope.deleteTrack = function(track) {
        /**
         * Deletes track from interface; if track already exists in database,
         * confirms before deletion and only deletes it from interface upon
         * successful deletion on backend.
         */
        if (track["id"] == null) {
            // null track["id"] means track is not yet in database
            $scope._removeTrackFromInterface(track)
        } else {
            // Confirm if the track already exists in the database
            var message = ("Are you sure you want to delete track \"" + track["name"] +
                "\"?  This will also delete any URLs associated with that track.");
            if ($window.confirm(message)) {
                // Delete track on backend
                $http.post(track["deleteURL"]).
                success(function(data, status, headers, config) {
                    $scope._removeTrackFromInterface(track)
                }).
                error(function(data, status, headers, config) {
                    $window.alert("An error occurred while deleting a track. Please try again.")
                });
            }
        }
    }
    
    $scope._removeTrackFromInterface = function(track) {
        /**
         * Removes the track from the list of tracks on the experiment,
         * causing it to be removed from the interface.
         *
         * Note: this function checks for a matching track by identity;
         * consequently you must pass the track itself, not just a copy of it
         * or an object with the same attributes. (i.e. you must pass by reference)
         */
        var i, len;
        for (i = 0, len = $scope.experiment.tracks.length; i < len; i ++) {
            if ($scope.experiment.tracks[i] == track) {
                // Delete it from the experiment
                $scope.experiment.tracks.splice(i, 1);
                break;
            }
        }
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
        if (orig.csvUpload != curr.csvUpload) { return true; }
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
        if (!confirmCancel || $window.confirm(message)) {
            $window.location = $window.parentPage;
        }
    }
    
    $scope.editTrackName = function(track) {
        /**
         * Set editing to true for the given track and false on all others
         */
        var i, len;
        for (i = 0, len = $scope.experiment.tracks.length; i < len; i ++) {
            $scope.experiment.tracks[i].editing = ($scope.experiment.tracks[i] == track);
        }
    }
    
    $scope.trackNameKeypress = function(event, track) {
        /**
         * handle [Enter] and [Esc] key presses from within the trackname edit box
         */
        if (event.keyCode == 13) {
            // [Enter] key saves
            $scope.trackNameChanged(track)
            event.preventDefault();
        } else if (event.keyCode == 27) {
            // [Esc] key cancels
            $scope.cancelTrackNameChange(track)
            event.preventDefault();
        }
    }
    
    $scope.cancelTrackNameChange = function(track) {
        /**
         * Cancel edits to a track name.
         */
        track.newName = track.name;
        track.editing = false;
    }
    
    $scope.isTrackOK = function(track) {
        /**
         * Check a new name for a track, returning true if OK and raising
         * an error and returning false if it is not.
         * Don't allow changing a track name to a name that is currently or was
         * originally used by a different track (the backend requires track
         * name uniqueness by experiment).
         */
        var i, len;
        for (i = 0, len = $scope.experiment.tracks.length; i < len; i ++) {
            var otherTrack = $scope.experiment.tracks[i];
            if (otherTrack == track) {
                continue;
            }
            if (otherTrack.name == track.newName || otherTrack.databaseName == track.newName ) {
                alert("Sorry, there is already another track with that name. Each track in an experiment must have a unique name.");
                return false;
            }
        }
        return true;
    }
    
    $scope.trackNameChanged = function(track) {
        /**
         * If new name is valid, set the track name and unset track editing.
         */
        if (track.newName == "" || !$scope.isTrackOK(track)) {
            $scope.cancelTrackNameChange(track);
        } else {
            track.name = track.newName;
            track.editing = false;
        }
    };
}



/**
 * Angular module configuration
 */
var app = angular.module('ABToolExperiment', []);
app.controller('experimentController', controller);
app.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);
