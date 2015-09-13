$(function() {
	var NUM_ACTIVITIES_PER_FETCH = 10;
	var filehashes = [];
	var activities_by_filehash = {};

	function fetch_activities(num_activities) {
		$.get('recents/fetch', function(data) {
			filehashes = filehashes.concat(data.filehashes)
			activities_by_filehash = $.extend(activities_by_filehash, data.activities_by_filehash);
			render_new_activities(data);
		});
	}

	function render_new_activities(data) {
		$.get('mustache/recents-item.html', function(template) {
			for(var filehash of data.filehashes) {
				var activity = data.activities_by_filehash[filehash];
				var ul = $('#recents-container');
				var view = {
					filehash: filehash,
					filename: activity.filename,
					thumb_path: activity.thumb_path
				};
				var rendered = Mustache.render(template, view)
                var tpl = $(rendered);
				data.context = tpl.appendTo(ul);
			}
		});
	}

	// fetch initial num activities.
	fetch_activities(NUM_ACTIVITIES_PER_FETCH); 
});