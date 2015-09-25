sharereadClient = {
	updateFile: (filehash, data) ->
		data = $.extend(data, {
			filehash: filehash
		})
		for key of data
			data[key] = JSON.stringify(data[key])
		$.post('file/update', data, (response) ->);
	,

	fetchFileMeta: (filehashes, callback) ->
		$.post('file/meta', {
			filehashes: JSON.stringify(filehashes),
		}, (response) ->
			sharereadStore.mergeFileMeta(response.meta_by_filehash)
			callback(response)
		)
	,

	fetchRecentFilehashes: (num_activities, callback) ->
		$.get('recents/fetch', (response) ->
			sharereadStore.mergeFileHashes(response.filehashes)
			sharereadStore.setActiveFilehashes(response.filehashes)
			# filehashes = filehashes.concat(data.filehashes)
			# activities_by_filehash = $.extend(activities_by_filehash, data.activities_by_filehash);
			callback(response)
		)
	,

	searchFile: (tags, callback) ->
		client = this
		$.post('search', {
			tags: JSON.stringify(tags),
			keywords: JSON.stringify("")
		}, (response) ->
			sharereadStore.setActiveFilehashes(response.filehashes)
			# fetch relavant meta data.
			client.fetchFileMeta(response.filehashes, (response) ->
				callback()
			)
		)
	,

	fetchRecents: (num_activities, callback) ->
		client = this;
		client.fetchRecentFilehashes(num_activities, (response) ->
			# fetch relavant meta data.
			client.fetchFileMeta(response.filehashes, (response) ->
				callback()
			)
		)
}