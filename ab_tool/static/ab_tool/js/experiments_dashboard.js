$(document).ready(function(){

    // *** IP MODALS *************************************************************************************************

    function validate_ip_name_input_element($name) {
        $name.toggleClass('has-error empty', !($name.val().trim()));
    }

    function validate_url_input_element($url) {
        // todo: consider using custom HTML5 validation with .willValidate() or .is(':valid') instead
        var urlValue = $url.val().trim();
        $url.toggleClass('empty', !urlValue);
        if ( is_valid_url(urlValue) ){
            $url.removeClass('has-error');
            $url.siblings('.preview-link').attr('href', urlValue).show();
        } else {
            $url.addClass('has-error');
            $url.siblings('.preview-link').hide();
        }
    }

    function is_valid_url(url) {
        //if URL input element is used, this should match the pattern attribute or the custom validation
        return /^(http(s)?:\/\/)?(www\.)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$/i.test(url);
    }

    function enable_submit_if_no_errors($form) {
        var formIsSubmittedPendingResponse = $form.find('.modal-submit').hasClass('submitting');
        var validationErrorsFound = $form.find('.has-error, .empty').length != 0;
        $form.find('.modal-submit').toggleClass('disabled', formIsSubmittedPendingResponse || validationErrorsFound);
    }

    function reset_IP_create_form($form) {
        $form.find('.form-control').val('');
        // .empty ensures that form cannot be submitted even though .has-error is not showing user validation feedback
        $form.find('.intervention-url, .intervention-name').removeClass('has-error').addClass('empty');
        // reset each selectmenu to the first item in the menu
        $form.find('select').each(function () {
            $($(this).siblings('ul').find('a')[0]).trigger('select');
        });
        enable_submit_if_no_errors($form);
    }

    function reset_IP_edit_form($form) {
        $form.find('.intervention-url, .intervention-name').each(function () {
            $(this).val($(this).data("initial-value"));
        });
        $form.find('.intervention-url').each(function(){
            validate_url_input_element($(this));
        });
        $form.find('.intervention-name').each(function(){
            validate_ip_name_input_element($(this));
        });
        $form.find('select').each(function () {
            $($(this).siblings('ul').find('a')[parseInt($(this).data("initial-index"))]).trigger('select');
        });
        enable_submit_if_no_errors($form);
    }

    // Initialize elements ****************************************************************************************

    // todo: consider updating to http://jqueryui.com/selectmenu/
    $('select').selectmenu({
        format: function(text){
            var pattern = /([\s\S]+)\-\- ([\s\S]+)/;
            var replacement = '<span class="option-title">$1</span><span class="option-description">$2</span>';
            return text.replace(pattern, replacement);
        }
    });

    $('[data-modal="intervention-new"]').each(function() {
        reset_IP_create_form($(this).find('.modal-form'));
    });

    $('[data-modal="intervention-edit"]').each(function() {
        reset_IP_edit_form($(this).find('.modal-form'));
    });

    // Set up event handlers ****************************************************************************************

    // multiple-submission protection for create/update button
    $('.modal-form').submit(function (event) {
        var $submit = $(this).find('.modal-submit');
        if ($submit.hasClass("disabled")) {
            event.preventDefault();
        }
        else {
            // disables create/update button, cancel button, and marks form for submit
            // (so that subsequent calls to enable_submit_if_no_errors will not re-enable form)
            $submit.addClass("disabled submitting");
            $submit.siblings('.modal-cancel').addClass("disabled");
        }
    });

    $('.intervention-url').on('input', function(){
        validate_url_input_element($(this));
        enable_submit_if_no_errors($(this).closest('.modal-form'));
    });

    $('.intervention-name').on('input', function () {
        validate_ip_name_input_element($(this));
        enable_submit_if_no_errors($(this).closest('.modal-form'));
    });

    // Reset the modal intervention point forms when they are dismissed (cancel, esc, submit, etc)
    // Note: show.bs.modal is triggered by all selectmenu clicks, so we reset the forms on hidden.bs.modal,
    //       as otherwise we have to check event target in show.bs.modal to avoid resetting on every click
    $('[data-modal="intervention-new"]').on('hidden.bs.modal', function() {
        reset_IP_create_form($(this).find('.modal-form'));
    });

    $('[data-modal="intervention-edit"]').on('hidden.bs.modal', function() {
        reset_IP_edit_form($(this).find('.modal-form'));
    });

    // *** DASHBOARD *******************************************************************************************

    $('[data-toggle="tooltip"]').tooltip();
});
