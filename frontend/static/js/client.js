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
	},


	fetchFileMeta: function(filehashes, callback) {
		$.post('file/meta', {
			filehashes: JSON.stringify(filehashes),
		}, function(response) {
			sharereadStore.mergeFileMeta(response.meta_by_filehash)
			callback(response);
		});
	},

	fetchRecentFilehashes: function(num_activities, callback) {
		$.get('recents/fetch', function(response) {
			sharereadStore.mergeFileHashes(response.filehashes);
			sharereadStore.setActiveFilehashes(response.filehashes);
			// filehashes = filehashes.concat(data.filehashes)
			// activities_by_filehash = $.extend(activities_by_filehash, data.activities_by_filehash);
			callback(response);
		});
	},

	searchFile: function(tags, callback) {
		$.post('search', {
			tags: JSON.stringify(tags),
			keywords: JSON.stringify("")
		}, function(response) {
			sharereadStore.setActiveFilehashes(response.filehashes);
			// fetch relavant meta data.
			client.fetchFileMeta(response.filehashes, function(response) {
				callback();
			});
		});
	},

	fetchRecents: function(num_activities, callback) {
		client = this;
		client.fetchRecentFilehashes(num_activities, function(response) {
			// fetch relavant meta data.
			client.fetchFileMeta(response.filehashes, function(response) {
				callback();
			});
		});
	}


};