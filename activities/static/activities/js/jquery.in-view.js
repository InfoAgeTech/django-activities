/**
 * Jquery plugin for checking if an element is in the viewport.
 * 
 * Examples
 * --------
 * Is the entire element in view:
 * 
 * > $('.obj').inView();
 * 
 * Is the top in view:
 * 
 * > $('.obj').inView('top');
 * 
 * Is the bottom in view:
 * 
 * > $('.obj').inView('bottom');
 */
(function ($) {
    
    $.fn.inView = function(inViewType){
        var viewport = {},
            bounds = {};
        viewport.top = $(window).scrollTop();
        viewport.bottom = viewport.top + $(window).height();
        bounds.top = this.offset().top;
        bounds.bottom = bounds.top + this.outerHeight();
        
        switch(inViewType) {
            case 'bottom':
                return ((bounds.bottom <= viewport.bottom) && (bounds.bottom >= viewport.top));
            case 'top':
                return ((bounds.top <= viewport.bottom) && (bounds.top >= viewport.top));         
            default:     
                return ((bounds.top >= viewport.top) && (bounds.bottom <= viewport.bottom));        
        }
    };
   
}(jQuery));
    