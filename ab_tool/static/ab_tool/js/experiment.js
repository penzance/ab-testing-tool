//(function($){

    function Experiment(expName, expSortType, expNotes){
        this.expName = expName;
        this.sortType = expSortType;
        this.notes = expNotes;

        //tracks object
        var tr = {};

        this.getTrObj = function(){
            return tr;
        }
        //counts the properties of the tr object
        this.trObjCount = function(){
            var count = 0;
            var i;

            for (i in tr){
                if ( tr.hasOwnProperty(i) ){
                    count++;
                }
            }
            return count;
        }

        //get all tracks names and values
        this.getTracks = function(){
            var allTracks = '';
            for (var property in tr) {
              allTracks += '<dt>' + property + '</dt><dd>' + tr[property]+ '</dd>';
            }
            return allTracks;
        }
        //add a track name and value
        this.addTracks = function(tname, tvalue){
            tr[tname] = tvalue;
        }
        //delete by track name
        this.deleteTrack = function(tname){
            delete tr[tname];
        }

        this.addTrackInput = function(DOMparent){
            
            var $newName = $('input#newTrackName').val();
            var $newWeight = $('input#newTrackWeight').val();
            //find the last track on list to get it's index
            //add one for newly created tracks
            var $newIndex = parseInt($('.expTrack').last().find('input').attr('data-trackindex')) + 1;
            //append new track to list-unstyled
            $(DOMparent).append(
                '<li class="expTrack">' +
                '<a href="#" data-track="delete">X</a> ' +
                '<input type="text" data-track="value" data-trackindex="' + $newIndex + '" id="track-' + $newIndex + '" maxlength="2" value="' + $newWeight + '" size="2"> % ' +
                '<label class="control-label" for="track-' + $newIndex + '"><span data-track="name" title="Edit track name">' + $newName + '</span></label>' +
                '</li>'
            );

            //clear the values
            $('input#newTrackWeight').val('').attr('placeholder', '0');
            $('input#newTrackName').val('').attr('placeholder', 'Enter track name');
        }

        this.deleteTrackInput = function(ele){
            $(ele).parent().remove();
        }

        this.isEquivalent = function(a, b) {
            // Create arrays of property names
            var aProps = Object.getOwnPropertyNames(a);
            var bProps = Object.getOwnPropertyNames(b);

            // If number of properties is different,
            // objects are not equivalent
            if (aProps.length != bProps.length) {
                return false;
            }

            for (var i = 0; i < aProps.length; i++) {
                var propName = aProps[i];

                // If values of same property are not equal,
                // objects are not equivalent
                if (a[propName] !== b[propName]) {
                    return false;
                }
            }

            // If we made it this far, objects
            // are considered equivalent
            return true;
        }

    }

//})(jQuery);
