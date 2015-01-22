describe("Tests for experimentController", function() {
    var $scope, $controller, controller, experiment;
    
    beforeEach(module('ABToolExperiment'));
    
    beforeEach(inject(function(_$controller_) {
        // The injector unwraps the underscores (_) from around the parameter names when matching
        $controller = _$controller_;
    }));
    
    beforeEach(function() {
        experiment = {
                "name": "", "notes": "", "uniformRandom": true,
                "tracks": [{"id": null, "name": "A", "newName": "A"},
                           {"id": null, "name": "B", "newName": "B"}]};
        $scope = {};
        controller = $controller('experimentController', { $scope: $scope });
        $scope.experiment = experiment;
    });
    
    describe("Tests for uniformPercent", function() {
        it("uniformPercent is 50 for two tracks", function() {
            expect($scope.uniformPercent()).toBe(50);
        });
        
        it("uniformPercent is 33 for three tracks", function() {
            $scope.experiment.tracks.push({});
            expect($scope.uniformPercent()).toBe(33);
        });
    });
    
    
    describe("Miscelaneous tests", function() {
        it("name is empty to start", function() {
            expect($scope.experiment.name).toBe("");
        });
        
//        it("test submit", function() {
//            $scope.submit();
//            expect($scope.experiment.name).toBe("");
//        });
    });
    

});

