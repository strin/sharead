sharereadStore = {
	activeFilehashes: [],
	filehashes: [],
	metaByFilehash: {},
	mergeFileHashes: function(filehashes) {
		this.filehashes = _.union(this.filehashes, filehashes)
	},
	setActiveFilehashes: function(activeFilehashes) {
		this.mergeFileHashes(activeFilehashes);
		this.activeFilehashes = activeFilehashes;
	},
	mergeFileMeta: function(metaByFilehash) {
		for(var filehash in metaByFilehash) {
			this.metaByFilehash = $.extend(this.metaByFilehash, metaByFilehash);
		}
	}
};