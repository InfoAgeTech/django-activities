// js handling for notifications.
$(document).ready(function(){
    
    function getLoadingHtml(){
        return '<div class="progress progress-striped active"><div class="progress-bar progress-bar-info bar">Loading...</div></div>';
    }

    
    /*
     * This is for notifications handling.
     *
     * Required data attributes:
     * 
     *  - data-ajax="notifications"
     *  
     * Usage:
     * 
     * <div data-ajax="notifications">...</div>
     */
    $('.notifications-container').on('click', '.notification .delete-notification form button',  function(e){
        var $frm = $(this).closest('form'),
            form_data = $frm.serialize();
        
        e.preventDefault(); 
        
        $.post($frm.attr('action'), form_data, function(resp_text, success_fail, resp){
            if (resp.status == 200){
                $frm.closest('.notification-container').remove();
            } else {
                console.log('There was an error deleting the notification.');
            }
        });
        
    }).on('click', '.notifications-paging .has-more', function(e){
        e.preventDefault();
        
        var $this = $(this),
            url = $this.attr('href');
        
        $this.replaceWith(getLoadingHtml());
        
        $.get(url, function(data){
            $('.notifications-paging').remove();
            $('ul.notifications:last').after(data);
        });
        
    }).on('click', 'ul.notification-type a', function(e){
        e.preventDefault();
        
        var $this = $(this),
            $parentType = $this.closest('.notification-type'),
            $parent = $this.closest('.notifications-container'),
            $notificationsContainer = $parent.find('.notifications:first'),
            $linkContainer = $this.closest('li'),
            url = $this.attr('href');
        
        if ($linkContainer.is('.active')) {
            // This is already active, nothing to do.
            return false;
        }
        
        $this.blur();        
        $parentType.find('li').removeClass('active');
        $linkContainer.addClass('active');
        
        $parent.find('.notifications-paging').remove();
        $notificationsContainer.html('<li class="notifications-paging">' + getLoadingHtml() + '</li>');
        
        $.get(url, function(data){
            $notificationsContainer.html(data);
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
            $notificationsContainer = $this.closest('.notifications-container')
            $text_input = $this.find('textarea[name="text"]'),
            form_data = $this.serialize();
        
        $.post($this.attr('action'), form_data, function(resp_text, success_fail, resp){
            var $notifications = $notificationsContainer.find('.notifications:first');
            
            if (resp.status == 200 || resp.status == 202) {
                $notifications.find('.no-notifications-found').remove();
                $notifications.prepend(resp_text.notification);
                $text_input.val('');
                $text_input.blur();
            } else {
                console.log('There was an error adding the comment.');
            }
        });
        
    }).on('submit', 'form.comment-reply-form', function(e){
        
        e.preventDefault();
        
        var $this = $(this),
            form_data = $this.serialize(),
            notification_id = $this.find('input[name="pid"]').val();
        
        $.post($this.attr('action'), form_data, function(resp_text, success_fail, resp){
            
            if (resp.status == 200 || resp.status == 202){
                $('#n-' + notification_id).replaceWith(resp_text.notification);
            } else {
                console.log('There was an error adding the notification reply.');
            }
        });
        
    }).on('submit', 'form.delete-notification', function(e){
        
        e.preventDefault();
        var $this = $(this),
            form_data = $this.serialize(),
            notification_id = $this.find('input[name="nid"]').val();
        
        $.post($this.attr('action'), form_data, function(resp_text, success_fail, resp){
            
            if (resp.status == 200){
                $('#n-' + notification_id).remove();
            } else {
                console.log('There was an error deleting the notification.');
            }
        });
    });
    
});
