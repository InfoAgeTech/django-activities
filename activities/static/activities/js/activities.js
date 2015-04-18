// js handling for activities.
$(document).ready(function(){
    
    function getLoadingHtml(){
        return '<div class="progress progress-striped active"><div class="progress-bar progress-bar-info bar">Loading...</div></div>';
    }

    
    /**
     * This is for activities handling.
     *
     * Required data attributes:
     * 
     *  - data-ajax="activities"
     *  
     * Usage:
     * 
     * <div data-ajax="activities">...</div>
     */
    $('.activities-container').on('click', '.activity .delete-activity form button',  function(e){
        var $frm = $(this).closest('form'),
            form_data = $frm.serialize();
        
        e.preventDefault(); 
        
        $.post($frm.attr('action'), form_data, function(resp_text, success_fail, resp){
            if (resp.status == 200){
                $frm.closest('.activity-container').remove();
            } else {
                console.log('There was an error deleting the activity.');
            }
        });
        
    }).on('click', '.activities-paging .has-more', function(e){
        e.preventDefault();
        
        var $this = $(this),
            url = $this.attr('href');
        
        $this.replaceWith(getLoadingHtml());
        
        $.get(url, function(data){
            $('.activities-paging').remove();
            $('ul.activities:last').after(data);
        });
        
    }).on('click', 'ul.activity-type a', function(e){
        e.preventDefault();
        
        var $this = $(this),
            $parentType = $this.closest('.activity-type'),
            $parent = $this.closest('.activities-container'),
            $activitiesContainer = $parent.find('.activities:first'),
            $linkContainer = $this.closest('li'),
            url = $this.attr('href');
        
        if ($linkContainer.is('.active')) {
            // This is already active, nothing to do.
            return false;
        }
        
        $this.blur();        
        $parentType.find('li').removeClass('active');
        $linkContainer.addClass('active');
        
        $parent.find('.activities-paging').remove();
        $activitiesContainer.append('<li class="activities-paging">' + getLoadingHtml() + '</li>');
        
        $.get(url, function(data){
            $activitiesContainer.html(data);
        });
        
    }).on('focus', 'form.comment-form textarea', function(e){
        e.preventDefault();
        var $this = $(this);
        
        if ($this.data('origHeight') == undefined){
            $this.data('origHeight', $this.css('height'));
        }
        
        $this.css('height', '75px');
        
    }).on('blur', 'form.comment-form textarea', function(e) {
        var $this = $(this);
        
        if ($.trim($this.val()) == ''){
            $this.css('height', $this.data('origHeight'));
        }
        
    }).on('submit', 'form.comment-form', function(e){
        e.preventDefault();
        var $this = $(this),
            $activitiesContainer = $this.closest('.activities-container')
            $textField = $this.find('textarea[name="text"]'),
            formData = $this.serialize(),
            text = $.trim($textField.val());
        
        if (!text) {
            // No text in the comment.  Nothing to do.
            return false;
        }
        
        $.post($this.attr('action'), formData, function(resp_text, success_fail, resp){
            var $activities = $activitiesContainer.find('.activities:first');
            
            if (resp.status == 200 || resp.status == 202) {
                $activities.find('.no-activities-found').remove();
                $activities.prepend(resp_text.activity);
                $textField.val('');
                $textField.blur();
            } else {
                console.log('There was an error adding the comment.');
            }
        });
        
    }).on('submit', 'form.comment-reply-form', function(e){
        
        e.preventDefault();
        
        var $this = $(this),
            form_data = $this.serialize(),
            activity_id = $this.find('input[name="pid"]').val(),
            text = $.trim($this.find('input[name="text"]').val());
        
        if (!text) {
            // No text in the comment.  Nothing to do.
            return false;
        }
        
        $.post($this.attr('action'), form_data, function(resp_text, success_fail, resp){
            
            if (resp.status == 200 || resp.status == 202){
                $('#n-' + activity_id).replaceWith(resp_text.activity);
            } else {
                console.log('There was an error adding the activity reply.');
            }
        });
        
    }).on('submit', 'form.delete-activity', function(e){
        
        e.preventDefault();
        var $this = $(this),
            form_data = $this.serialize(),
            activity_id = $this.find('input[name="nid"]').val();
        
        $.post($this.attr('action'), form_data, function(resp_text, success_fail, resp){
            
            if (resp.status == 200){
                $('#n-' + activity_id).remove();
            } else {
                console.log('There was an error deleting the activity.');
            }
        });
    });
    
});
