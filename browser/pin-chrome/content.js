var url = window.location.href;
//// make sure this is a pdf link.
// if(url.indexOf('.pdf') == -1) {
// 	console.log('papertroll: this is not a pdf!');
// }
$.post('http://54.149.190.97:8899/pin-submit', {
	'link': url
}, function() {

});