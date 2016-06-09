// Generated by CoffeeScript 1.10.0
(function() {
  var indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  $(function() {
    var NUM_ACTIVITIES_PER_FETCH, client, render_activities, store;
    NUM_ACTIVITIES_PER_FETCH = 10;
    client = window.sharereadClient;
    store = sharereadStore;
    render_activities = function() {
      return $.get('mustache/recents-item.html', function(template) {
        var activity, filehash, fileid, i, len, ref, rendered, toggleLink, tpl, ul, view;
        $('#recents-container').html("");
        fileid = 0;
        ref = store.activeFilehashes;
        for (i = 0, len = ref.length; i < len; i++) {
          filehash = ref[i];
          activity = store.metaByFilehash[filehash];
          ul = $('#recents-container');
          view = {
            filehash: filehash,
            fileid: fileid,
            filename: activity.filename,
            thumb_path: activity.thumb_path,
            tags: store.miscInfo['all_tags'].map(function(tag) {
              return {
                'tag': tag,
                'selected': indexOf.call(activity.tags, tag) >= 0 ? 'selected' : ''
              };
            })
          };
          console.log('activity', activity);
          console.log('view', view);
          rendered = Mustache.render(template, view);
          tpl = $(rendered);
          tpl.appendTo(ul);
          tpl.find('.recents-tag').change((function(tpl, filehash) {
            var chosen, dataChosen, tagsChosen;
            chosen = tpl.find('.recents-tag').data('chosen');
            dataChosen = _.filter(chosen.results_data, function(data) {
              return data.selected;
            });
            tagsChosen = _.map(dataChosen, function(data) {
              return data.text;
            });
            return sharereadClient.updateFile(filehash, {
              tags: tagsChosen
            });
          }).bind(this, tpl, filehash));
          tpl.mouseenter((function(tpl) {
            var details;
            details = tpl.find('.recents-details');
            details.removeClass('recents-details-hide');
            return details.addClass('recents-details-show');
          }).bind(this, tpl));
          tpl.mouseleave((function(tpl) {
            var details;
            details = tpl.find('.recents-details');
            details.removeClass('recents-details-show');
            return details.addClass('recents-details-hide');
          }).bind(this, tpl));
          toggleLink = function(el) {
            if (el.attr('href')) {
              el.data('href', el.attr('href'));
              return el.removeAttr('href');
            } else {
              return el.attr('href', el.data('href'));
            }
          };
          tpl.find('.recents-edit-btn').click((function(tpl) {
            if (tpl.find('.recents-item-filename').prop('disabled') === true) {
              toggleLink(tpl.find('.anchor'));
              tpl.find('.recents-item-filename').prop('disabled', false);
              tpl.find('.recents-item-filename').select();
            } else {
              toggleLink(tpl.find('.anchor'));
              tpl.find('.recents-item-filename').prop('disabled', true);
            }
            return tpl.find('.recents-edit-btn').toggleClass('glyphicon-red');
          }).bind(this, tpl));
          tpl.find('#filename').change((function(tpl, filehash) {
            var filename;
            filename = tpl.find('#filename')[0].value;
            return $.post('file/update', {
              filename: JSON.stringify(filename),
              filehash: JSON.stringify(filehash)
            }, function(data) {});
          }).bind(this, tpl, filehash));
          tpl.mouseleave();
          fileid += 1;
        }
        return $('.recents-tag.chosen-select').chosen({
          create_option: true,
          skip_no_results: true,
          hide_selected: true
        });
      });
    };
    client.fetchMiscInfo(function() {
      var searchbar;
      client.fetchRecents(NUM_ACTIVITIES_PER_FETCH, render_activities);
      $('#searchbar_selector').html(store.miscInfo['all_tags'].map(function(tag) {
        return Mustache.render("<option value='{{tag}}'>{{tag}}</option>", {
          tag: tag
        });
      }).join('\r\n'));
      return searchbar = $('.searchbar .chosen-select').searchbar({
        skip_no_results: true,
        hide_selected: true
      });
    });
    return $('#searchbar_selector').change(function() {
      var chosen, dataChosen, tagsChosen;
      chosen = $('.searchbar .chosen-select').data('chosen');
      dataChosen = _.filter(chosen.results_data, function(data) {
        return data.selected;
      });
      tagsChosen = _.map(dataChosen, function(data) {
        return data.text;
      });
      if (tagsChosen.length > 0) {
        return sharereadClient.searchFile(tagsChosen, render_activities);
      } else {
        return sharereadClient.fetchRecents(NUM_ACTIVITIES_PER_FETCH, render_activities);
      }
    });
  });

}).call(this);
