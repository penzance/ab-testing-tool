$(document).ready(function(){

    // multiple-submission protection for create/update button
    $('.modal-form').submit(function (event) {
        var $submit_button = $(this).find('.modal-submit');
        if ($submit_button.hasClass("disabled")) {
            event.preventDefault();
        }
        else {
            // disables create/update button, cancel button
            $submit_button.addClass("disabled");
            $submit_button.siblings('.modal-cancel').addClass("disabled");
        }
    });

    function is_valid_url(url) {
        return /^(http(s)?:\/\/)?(www\.)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$/i.test(url);
    }

    $('.addIntervention').modal('show');

    // TODO: if we're still using Scott Jehl's, consider updating to http://jqueryui.com/selectmenu/
    // http://www.filamentgroup.com/lab/jquery-ui-selectmenu-an-aria-accessible-plugin-for-styling-a-html-select.html
    $('select').selectmenu({
        format: function(text){
            var pattern = /([\s\S]+)\-\- ([\s\S]+)/;
            var replacement = '<span class="option-title">$1</span><span class="option-description">$2</span>';
            return text.replace(pattern, replacement);
        }
    });
    
    //for showing preview buttons when creating or editgin and intervention point
    // todo: remove .modal-intervention from template if we can use data-modal for everything
    $('[data-modal="intervention-edit"], [data-modal="intervention-new"]').on('show.bs.modal', function (e) {

        //go through each track url to show/hide preview link
        $('.intervention-url').each(function(i){
            //on modal show we validate and show the preview
            if ( is_valid_url( $(this).val().trim() ) ){
                $(this)
                    .siblings('.preview-link')
                    .attr({
                        href:$(this).val().trim(),
                        target: '_blank'
                    });
            }else{
                $(this).siblings('.preview-link').hide();
            }
            
            //as they change the input url field
            $(this).on('input', function(){
                if ( is_valid_url( $(this).val().trim() ) ){
                    
                    if ( $(this).siblings('.preview-link').is(":hidden") ){
                        $(this).siblings('.preview-link').show();
                    }

                    $(this)
                        .siblings('.preview-link')
                        .attr({
                            href:$(this).val().trim(),
                            target: '_blank'
                        });
                }else{
                    $(this).siblings('.preview-link').hide();
                }
                
            });

        });//end each

        //e.currentTarget = references the modal window that's open
        var $currentModal = $(e.currentTarget);
        //find the intervention name for the window that's open
        var $interventionName = $currentModal.find('.intervention-name');

        //disable the create button if IP name is empty
        //this is mostly for new IP
        if ( !$.trim( $interventionName.val() ).length ){
            $currentModal.find('button').addClass('disabled');
        }
        
        //update error class and able/disabled button as the user
        //changes the intervention name input
        $interventionName.on('input', function(){
            if ( $.trim( $(this).val() ).length ){
                $currentModal.find('button').removeClass('disabled');
                if ( $(this).hasClass('has-error') ){
                    $(this).removeClass('has-error');
                }
            }else{
                $currentModal.find('button').addClass('disabled');
                $(this).addClass('has-error');
            }
        });

    });
    

    $('[data-toggle="tooltip"]').tooltip();
});
