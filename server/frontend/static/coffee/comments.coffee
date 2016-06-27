# load comments on page load

# annotate paper with comments
# visual hint: yellow underline
# event: on click, open comments panel, jump to corresponding part, hightlight corresponding comment by showing a visual line near it

$ ->
	$('#toolbar').click(->
		$('comments').toggle()
	)