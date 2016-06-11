$ ->
	NUM_ACTIVITIES_PER_FETCH = 10
	render_activities = -> 
		$.get('mustache/recents-item.html',
			(template) ->
				# clear container.
				$('#recents-container').html("")
				# render items.
				fileid = 0
				for filehash in store.activeFilehashes
					activity = store.metaByFilehash[filehash]
					ul = $('#recents-container')
					view = {
						filehash: filehash
						fileid: fileid
						filename: activity.filename
						thumb_path: activity.thumb_path
						tags: store.miscInfo['all_tags'].map((tag) ->
								return {
									'tag': tag
									'selected': if tag in activity.tags then 'selected' else ''
								}
							)
					}
					console.log('activity', activity)
					console.log('view', view)
					rendered = Mustache.render(template, view)
					tpl = $(rendered)
					tpl.appendTo(ul)

					# on select change, send new tags to server.
					tpl.find('.recents-tag').change(((tpl, filehash) ->
						# get list of all tags.
						chosen = tpl.find('.recents-tag').data('chosen')
						dataChosen = _.filter(chosen.results_data, 
							(data) ->
								return data.selected
						)
						tagsChosen = _.map(dataChosen, 
							(data) ->
								return data.text
						)
						client.updateFile(filehash, {
							tags: tagsChosen
						})
					).bind(this, tpl, filehash))

					# on hover, show more details.
					tpl.mouseenter(((tpl) ->
						details = tpl.find('.recents-details')
						details.removeClass('recents-details-hide')
						details.addClass('recents-details-show')
					).bind(this, tpl))

					# on mouse out, hide the details.
					tpl.mouseleave(((tpl) ->
						details = tpl.find('.recents-details')
						details.removeClass('recents-details-show')
						details.addClass('recents-details-hide')
					).bind(this, tpl))

					# on click edit button, toggle edit mode.
					toggleLink = (el) ->
						if(el.attr('href'))
							el.data('href', el.attr('href'))
							el.removeAttr('href')
						else
							el.attr('href', el.data('href'))

					tpl.find('.recents-edit-btn').click(((tpl) ->
						if(tpl.find('.recents-item-filename').prop('disabled') == true)
							toggleLink(tpl.find('.anchor'))
							tpl.find('.recents-item-filename').prop('disabled', false)
							tpl.find('.recents-item-filename').select()
						else
							toggleLink(tpl.find('.anchor'))
							tpl.find('.recents-item-filename').prop('disabled', true)
						tpl.find('.recents-edit-btn').toggleClass('glyphicon-red')
					).bind(this, tpl))

					# on change filename.
					tpl.find('#filename').change(((tpl, filehash) ->
	                    filename = tpl.find('#filename')[0].value
	                    $.post('file/update', {
	                        filename: JSON.stringify(filename),
	                        filehash: JSON.stringify(filehash)
	                    }, (data) ->

	                    )
	                 ).bind(this, tpl, filehash))


					tpl.mouseleave()

					fileid += 1

				# activate chosen select plugins.
				$('.recents-tag.chosen-select').chosen({
					create_option: true,
					skip_no_results: true
					hide_selected: true
				})
		)
	

	# fetch db misc.
	client.fetchMiscInfo ->
		# fetch initial num activities.
		client.fetchRecents(NUM_ACTIVITIES_PER_FETCH, render_activities)
		# initialize search bar.
		$('#searchbar_selector').html(store.miscInfo['all_tags'].map((tag) ->
			return Mustache.render("<option value='{{tag}}'>{{tag}}</option>", {tag: tag})
		).join('\r\n'))
		searchbar = $('.searchbar .chosen-select').searchbar({
			skip_no_results: true,
			hide_selected: true
		})

	$('#searchbar_selector').change(() ->
		# searchbar change event.
		chosen = $('.searchbar .chosen-select').data('chosen')
		dataChosen = _.filter(chosen.results_data, (data) ->
			return data.selected;
		)
		tagsChosen = _.map(dataChosen, (data) ->
			return data.text;
		)

		if(tagsChosen.length > 0) # do filter.
			client.searchFile(tagsChosen, render_activities)
		else
			client.fetchRecents(NUM_ACTIVITIES_PER_FETCH, render_activities)
	)