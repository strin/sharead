sharereadClient = {
	updateFile: function(filehash, data) {
		data = $.extend(data, {
			filehash: filehash
		});
		for(var key in data) {
			data[key] = JSON.stringify(data[key]);
		}
		$.post('file/update', data, 
			function(response) {

			}
		);
	}
};