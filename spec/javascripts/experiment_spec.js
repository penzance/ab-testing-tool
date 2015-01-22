describe("Tests for experiment", function() {
    var $scope, $controller, controller, experiment;
    
    beforeEach(module('ABToolExperiment'));
    
    beforeEach(inject(function(_$controller_) {
        // The injector unwraps the underscores (_) from around the parameter names when matching
        $controller = _$controller_;
    }));
    
    describe('experimentController', function() {
        beforeEach(function() {
            experiment = {
                    "name": "", "notes": "", "uniformRandom": true,
                    "tracks": [{"id": null, "name": "A", "newName": "A"},
                               {"id": null, "name": "B", "newName": "B"}]};
            $scope = {};
            controller = $controller('experimentController', { $scope: $scope });
            $scope.experiment = experiment;
        });
        
        it("name is empty to start", function() {
            expect($scope.experiment.name).toBe("");
        });
        
        it("uniformPercent is 50 for two tracks", function() {
            expect($scope.uniformPercent()).toBe(50);
        });
    });
});

