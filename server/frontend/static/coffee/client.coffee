window.client = {
	updateFile: (filehash, data) ->
		data = $.extend(data, {
			filehash: filehash
		})
		for key of data
			data[key] = JSON.stringify(data[key])
		$.post('file/update', data, (response) ->);
	,

	fetchFileMeta: (filehashes, callback) ->
		# ignore filehash already in meta_by_filehash.
		new_filehashes = []
		for filehash in filehashes
			if filehash in store.metaByFilehash
				continue
			new_filehashes.push(filehash)
		$.post('file/meta', {
			filehashes: JSON.stringify(filehashes),
		}, (response) ->
			store.mergeFileMeta(response.meta_by_filehash)
			callback(response)
		)
	,

	fetchRecentFilehashes: (num_activities, callback) ->
		$.get('recents/fetch', (response) ->
			store.mergeFileHashes(response.filehashes)
			store.setActiveFilehashes(response.filehashes)
			# filehashes = filehashes.concat(data.filehashes)
			# activities_by_filehash = $.extend(activities_by_filehash, data.activities_by_filehash);
			callback(response)
		)
	,

	fetchMiscInfo: (callback) ->
		$.get('db/misc', (response) ->
			console.log('misc', response)
			store.setMiscInfo(response)
			callback()
		)
	,

	searchFile: (tags, keywords, callback) ->
		client = this
		$.post('search', {
			tags: JSON.stringify(tags),
			keywords: JSON.stringify(keywords)
		}, (response) ->
			store.setActiveFilehashes(response.filehashes)
			# fetch relavant meta data.
			client.fetchFileMeta(response.filehashes, (response) ->
				callback()
			)
		)
	,

	fetchHTMLView: (static_url, callback) ->
		client = this
		$.get(static_url, {}, (response) ->
			callback(response);
		)


	fetchRecents: (num_activities, callback) ->
		client = this;
		client.fetchRecentFilehashes(num_activities, (response) ->
			# fetch relavant meta data.
			client.fetchFileMeta(response.filehashes, (response) ->
				callback()
			)
		)
}