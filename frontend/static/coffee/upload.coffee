$ -> 
    ul = $('#upload ul')

    $('#drop a').click(->
        # Simulate a click on the file input button
        # to show the file browser dialog
        $(this).parent().find('input').click()
    )

    # Initialize the jQuery File Upload plugin
    $('#upload').fileupload({

        # This element will accept file drag / drop uploading
        dropZone: $('#drop'),

        done: (e, data) ->
            data.context.find('#filename')[0].dataset.filehash = data.result.filehash
            data.context.find('#filename')[0].value = data.result.filename
            window.location.href = 'recents'
        ,
        
        # This function is called when a file is added to the queue;
        # either via the browse button, or via drag/drop:
        add: (e, data) ->
            $.get('mustache/uploaded-item.html', (template) ->
                view = {
                    filename: data.files[0].name,
                    filesize: formatFileSize(data.files[0].size)
                }

                rendered = Mustache.render(template, view)
                tpl = $(rendered);

                # Add the HTML to the UL element
                data.context = tpl.appendTo(ul)

                # Initialize the knob plugin
                tpl.find('#progress').knob()

                # Listen for clicks on the cancel icon
                tpl.find('span').click(->
                    if tpl.hasClass('working')
                        jqXHR.abort()

                    tpl.fadeOut(->
                        tpl.remove()
                    )
                )

                # Listen for filename changes.
                tpl.find('#filename').change(->
                    filename = tpl.find('#filename')[0].value
                    filehash = tpl.find('#filename')[0].dataset.filehash
                    $.post('file/update', {
                        filename: JSON.stringify(filename),
                        filehash: JSON.stringify(filehash)
                    }, (data) ->

                    )
                )

                tpl.find("#filename").keyup((event) ->
                    if event.keyCode == 13
                        $(this).blur()
                )

                # Automatically upload the file once it is added to the queue
                jqXHR = data.submit()
            )
        ,

        progress: (e, data) ->

            # Calculate the completion percentage of the upload
            progress = parseInt(data.loaded / data.total * 100, 10);

            # Update the hidden progress field and trigger a change
            # so that the jQuery knob plugin knows to update the dial
            data.context.find('#progress').val(progress).change()

            if progress == 100
                data.context.removeClass('working')
        ,

        fail: (e, data) ->
            # Something has gone wrong!
            data.context.addClass('error')
    })


    # Prevent the default action when a file is dropped on the window
    $(document).on('drop dragover', (e) ->
        e.preventDefault()
    )

    # Helper function that formats the file sizes
    formatFileSize = (bytes) ->
        if typeof bytes != 'number'
            return ''

        if (bytes >= 1000000000)
            return (bytes / 1000000000).toFixed(2) + ' GB'

        if (bytes >= 1000000)
            return (bytes / 1000000).toFixed(2) + ' MB';

        return (bytes / 1000).toFixed(2) + ' KB';
