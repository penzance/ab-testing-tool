var controller = function($scope, $window, $http) {
    /**
     * Angular controller (attached to angular module at bottom of file)
     */
    
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
    
    $scope.submit = function() {
        /**
         * Submits form contents to the backend and redirects to window.parentPage
         */
        // Payload has to be encoded using JQuery's $.param to submit properly
        //var payload = $.param({"experiment": JSON.stringify($scope.experiment)});
        $http.post($window.submitURL, $scope.experiment).
          success(function(data, status, headers, config) {
              $window.location = $window.parentPage;
          }).
          error(function(data, status, headers, config) {
              $window.alert("An error occured submitting this form")
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
                "\"?  This will also delete any URLs associrated with that track.");
            if ($window.confirm(message)) {
                // Delete track on backend
                $http.post(track["deleteURL"]).
                success(function(data, status, headers, config) {
                    $scope._removeTrackFromInterface(track)
                }).
                error(function(data, status, headers, config) {
                    $window.alert("An error occured deleting a track")
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
    
    $scope.trackNameChanged = function(track) {
        /**
         * Check a new name for a track and if it is valid, set the track name.
         * Don't allow changing a track name to a name that is currently or was
         * originally used by a different track (the backend requires track
         * name uniqueness by experiment).
         */
        console.log(track.newName);
        if (track.newName == "") {
            track.newName = track.name;
        }
        var i, len;
        for (i = 0, len = $scope.experiment.tracks.length; i < len; i ++) {
            var otherTrack = $scope.experiment.tracks[i];
            if (otherTrack == track) {
                continue;
            }
            if (otherTrack.name == track.newName) {
                alert("Invalid Name: There is another track with that name");
                track.newName = track.name;
                return;
            } else if (otherTrack.originalName == track.newName) {
                alert("Invalid Name: There was already another track with that name");
                track.newName = track.name;
                return;
            }
        }
        track.name = track.newName;
    };
}


contenteditable = function() {
    /**
     * Directive to allow ng-model to work with contenteditable attribute
     * (attached to angular module at bottom of file)
     */
    var linkFunction = function(scope, element, attrs, ngModel) {
        if (!ngModel) {
            return; // do nothing if no ng-model
        }
        
        // when model changes, update view
        ngModel.$render = function() {
            element.html(ngModel.$viewValue || "");
        };
        
        setView = function() {
            ngModel.$setViewValue(element.html());
        };
        
        // when view changes, update model
        element.on('blur', function() {
            scope.$apply(setView);
        });
        
        element.on('keydown', function($event) {
            // handle [Enter] and [Esc] key presses from within the trackname
            if ($event.keyCode == 13) {
                // [Enter] key saves
                element.blur();
            } else if ($event.keyCode == 27) {
                // [Esc] key saves
                element.blur();
            }
        });
        
        // initialize
        setView();
    };
    
    return {require: '?ngModel', link: linkFunction};
}

/**
 * Angular module configuration
 */
angular.module('ABToolExperiment', []).
    controller('experimentController', controller).
    directive('contenteditable', contenteditable);