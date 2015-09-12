$(function(){

    var ul = $('#upload ul');

    $('#drop a').click(function(){
        // Simulate a click on the file input button
        // to show the file browser dialog
        $(this).parent().find('input').click();
    });

    // Initialize the jQuery File Upload plugin
    $('#upload').fileupload({

        // This element will accept file drag/drop uploading
        dropZone: $('#drop'),

        done: function(e, data) {
            console.log(data.context);
            data.context.find('#filename')[0].dataset.filehash = data.result.filehash
        },

        // This function is called when a file is added to the queue;
        // either via the browse button, or via drag/drop:
        add: function (e, data) {
            $.get('mustache/uploaded-item.html', function(template) {
                var view = {
                    filename: data.files[0].name,
                    filesize: formatFileSize(data.files[0].size)
                };

                var rendered = Mustache.render(template, view)
                var tpl = $(rendered);

                // Add the HTML to the UL element
                data.context = tpl.appendTo(ul);

                // Initialize the knob plugin
                tpl.find('#progress').knob();

                // Listen for clicks on the cancel icon
                tpl.find('span').click(function(){

                    if(tpl.hasClass('working')){
                        jqXHR.abort();
                    }

                    tpl.fadeOut(function(){
                        tpl.remove();
                    });

                });

                // Listen for filename changes.
                tpl.find('#filename').change(function() {
                    var filename = tpl.find('#filename')[0].value;
                    var filehash = tpl.find('#filename')[0].dataset.filehash;
                    $.post('file/update', {
                        filename: JSON.stringify(filename),
                        filehash: JSON.stringify(filehash)
                    }, function(data) {

                    });
                });

                tpl.find("#filename").keyup(function(event){
                    if(event.keyCode == 13){
                        $(this).blur();
                    }
                });

                // Automatically upload the file once it is added to the queue
                var jqXHR = data.submit();
            });
        },

        progress: function(e, data){

            // Calculate the completion percentage of the upload
            var progress = parseInt(data.loaded / data.total * 100, 10);

            // Update the hidden progress field and trigger a change
            // so that the jQuery knob plugin knows to update the dial
            data.context.find('#progress').val(progress).change();

            if(progress == 100){
                data.context.removeClass('working');
            }
        },

        fail:function(e, data){
            // Something has gone wrong!
            data.context.addClass('error');
        }

    });


    // Prevent the default action when a file is dropped on the window
    $(document).on('drop dragover', function (e) {
        e.preventDefault();
    });

    // Helper function that formats the file sizes
    function formatFileSize(bytes) {
        if (typeof bytes !== 'number') {
            return '';
        }

        if (bytes >= 1000000000) {
            return (bytes / 1000000000).toFixed(2) + ' GB';
        }

        if (bytes >= 1000000) {
            return (bytes / 1000000).toFixed(2) + ' MB';
        }

        return (bytes / 1000).toFixed(2) + ' KB';
    }

});


