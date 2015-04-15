describe("Tests for edit_intervention_point", function() {

    describe("Tests for set_preview_href()", function() {
        //TODO
        it("tests that true equals true", function() {
            expect(true).toBe(true);
        });
    });

});

describe("Tests for experiments_dashboard", function() {

    describe("Tests for isValidUrl()", function() {
        it("tests that a valid http url passes validator", function() {
            expect(isValidUrl("http://www.example.com")).toBe(true);
        });
        it("tests that a valid https url passes validator", function() {
            expect(isValidUrl("https://www.example.com")).toBe(true);
        });
        it("tests that an invalid url missing http does not pass validator", function() {
            expect(isValidUrl("www.example.com")).toBe(false);
        });
        it("tests that an invalid url does not pass", function() {
            expect(isValidUrl("http//www.example.com")).toBe(false);
        });
        it("tests that an invalid url does not pass", function() {
            expect(isValidUrl("http://wwwexasdfasdfsafdasf")).toBe(false);
        });
        it("tests that an invalid does not pass", function() {
            expect(isValidUrl("https:/www.example.com")).toBe(false);
        });
    });
});

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
    
    describe("Miscellaneous tests", function() {
        it("name is empty to start", function() {
            expect($scope.experiment.name).toBe("");
        });
        
        it("test that submitting is true on submit", function() {
            $scope.submit();
            expect($scope.submitting).toBe(true);
        });
    });
});

