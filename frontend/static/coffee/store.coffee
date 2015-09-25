sharereadStore = {
	activeFilehashes: [],
	filehashes: [],
	metaByFilehash: {},
	miscInfo: {},

	mergeFileHashes: (filehashes) ->
		@filehashes = _.union(@filehashes, filehashes)

	setActiveFilehashes: (activeFilehashes) ->
		@mergeFileHashes(activeFilehashes)
		@activeFilehashes = activeFilehashes
	
	mergeFileMeta: (metaByFilehash) ->
		for filehash of metaByFilehash
			@metaByFilehash = $.extend(@metaByFilehash, metaByFilehash)	

	setMiscInfo: (miscInfo) ->
		@miscInfo = $.extend(@miscInfo, miscInfo)
};