sharereadStore = {
	activeFilehashes: [],
	filehashes: [],
	metaByFilehash: {},

	mergeFileHashes: (filehashes) ->
		@filehashes = _.union(@filehashes, filehashes)

	setActiveFilehashes: (activeFilehashes) ->
		@mergeFileHashes(activeFilehashes)
		@activeFilehashes = activeFilehashes
	
	mergeFileMeta: (metaByFilehash) ->
		for filehash of metaByFilehash
			@metaByFilehash = $.extend(@metaByFilehash, metaByFilehash)	
};