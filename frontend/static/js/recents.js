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
			// render items.
			var fileid = 0;
			for(var filehash of data.filehashes) {
				var activity = data.activities_by_filehash[filehash];
				var ul = $('#recents-container');
				var view = {
					filehash: filehash,
					fileid: fileid,
					filename: activity.filename,
					thumb_path: activity.thumb_path 
				};
				var rendered = Mustache.render(template, view)
                var tpl = $(rendered);
				data.context = tpl.appendTo(ul);

				// on select change, send new tags to server.
				tpl.find('.recents-tag').change(_.bind(function(tpl, filehash) {
					// get list of all tags.
					var tags = $.map(tpl.find('.recents-tag')[0].children, function(child) {
						return child.value;
					});
					var selectorId = tpl.find('.recents-tag')[0].id;
					var selectorIdChosen = selectorId + '_chosen';
					var closeActions = tpl.find('#' + selectorIdChosen + ' .chosen-choices .search-choice .search-choice-close');
					var tagsChosen = $.map(closeActions, function(action) {
						var index = action.dataset.optionArrayIndex;
						return tags[index];
					});
					console.log('tagsChosen', tagsChosen);
					sharereadClient.updateFile(filehash, {
						tags: tagsChosen
					});
				}, {}, tpl, filehash));

				// on hover, show more details.
				tpl.mouseenter(_.bind(function(tpl) {
					var details = tpl.find('.recents-details');
					details.removeClass('recents-details-hide');
					details.addClass('recents-details-show');
				}, {}, tpl));

				// on mouse out, hide the details.
				tpl.mouseleave(_.bind(function(tpl) {
					var details = tpl.find('.recents-details');
					details.removeClass('recents-details-show');
					details.addClass('recents-details-hide');
				}, {}, tpl));

				tpl.mouseleave();

				fileid += 1;
			}
			// activate chosen select plugins.
			$('.recents-tag.chosen-select').chosen({
				create_option: true,
				skip_no_results: true
			});
		});
	}

	// fetch initial num activities.
	fetch_activities(NUM_ACTIVITIES_PER_FETCH); 

	// initialize search bar.
	$('.searchbar .chosen-select').searchbar({
		skip_no_results: true
	});
});