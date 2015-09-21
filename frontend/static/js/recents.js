$(function() {
	var NUM_ACTIVITIES_PER_FETCH = 10;
	var client = sharereadClient;
	var store = sharereadStore;

	function render_activities() {
		$.get('mustache/recents-item.html', function(template) {
			// clear container.
			$('#recents-container').html("");
			// render items.
			var fileid = 0;
			for(var filehash of store.activeFilehashes) {
				var activity = store.metaByFilehash[filehash];
				var ul = $('#recents-container');
				var view = {
					filehash: filehash,
					fileid: fileid,
					filename: activity.filename,
					thumb_path: activity.thumb_path 
				};
				var rendered = Mustache.render(template, view)
                var tpl = $(rendered);
                tpl.appendTo(ul);

				// on select change, send new tags to server.
				tpl.find('.recents-tag').change(_.bind(function(tpl, filehash) {
					// get list of all tags.
					var chosen = tpl.find('.recents-tag').data('chosen');
					var dataChosen = _.filter(chosen.results_data, function(data) {
						return data.selected;
					});
					var tagsChosen = _.map(dataChosen, function(data) {
						return data.text;
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
	client.fetchRecents(NUM_ACTIVITIES_PER_FETCH, render_activities);

	// initialize search bar.
	var searchbar = $('.searchbar .chosen-select').searchbar({
		skip_no_results: true
	});

	$('#searchbar_selector').change(function() {
		// searchbar change event.
		var chosen = $('.searchbar .chosen-select').data('chosen');
		var dataChosen = _.filter(chosen.results_data, function(data) {
			return data.selected;
		});
		var tagsChosen = _.map(dataChosen, function(data) {
			return data.text;
		});

		if(tagsChosen.length > 0) { // do filter.
			sharereadClient.searchFile(tagsChosen, render_activities);	
		}else{
			sharereadClient.fetchRecents(NUM_ACTIVITIES_PER_FETCH, render_activities);
		}
		
		// var tags = $.map($('#searchbar_selector')[0].children, function(child) {
		// 	return child.value;
		// });
		// var closeActions = $('#searchbar_selector_chosen .chosen-choices .search-choice .search-choice-close');
		// console.log('closeActions', closeActions);
		// var tagsChosen = $.map(closeActions, function(action) {
		// 	var index = action.dataset.optionArrayIndex;
		// 	return tags[index];
		// });
		// console.log(tagsChosen);
	});
});