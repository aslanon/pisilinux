$(document).ready(function() {
	$("#slideshow").css("overflow", "hidden");
	
	$("ul#slides").cycle({
        fx: 'scrollRight',
		pause: 1,
		prev: '#prev',
		next: '#next',
		speed: "800",
		timeout: "2500"
	});
	
	$("#slideshow").hover(function() {
        $("ul#nav").fadeIn();      
  	},
  		function() {
    	$("ul#nav").fadeOut();
  	});
	
});
