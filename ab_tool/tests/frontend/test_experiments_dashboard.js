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
