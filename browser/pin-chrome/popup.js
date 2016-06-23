// Copyright (c) 2012 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

// Store CSS data in the "local" storage area.
//
// See note in options.js for rationale on why not to use "sync".
var storage = chrome.storage.local;

var message = document.querySelector('#message');

var url = null;


// Check if there is CSS specified.
storage.get('css', function(items) {
  console.log(items);
  // If there is CSS specified, inject it into the page.
  // if (items.css) {
  //   chrome.tabs.insertCSS({code: items.css}, function() {
  //     if (chrome.runtime.lastError) {
  //       message.innerText = 'Not allowed to inject CSS into special page.';
  //     } else {
  //       message.innerText = 'Injected style!';
  //     }
  //   });
  // } else {
  //   var optionsUrl = chrome.extension.getURL('options.html');
  //   message.innerHTML = 'Set a style in the <a target="_blank" href="' +
  //       optionsUrl + '">options page</a> first.';
  // }



  // submit_pin();
  var pin = document.getElementById('pin');
  pin.addEventListener('click', submit_pin);
  message.innerHTML = pin;
});


function submit_pin() {
  
  var cookie = localStorage.getItem('sharead-cookie');

  if(cookie) {
    chrome.tabs.getSelected(null,function(tab) {
      $.post('http://sharead-org.herokuapp.com/pin-submit', {
       'link': tab.url,
       'cookie': cookie
      }, function() {

      });
    });
    
  }else{
    chrome.identity.getAuthToken({
        interactive: true
    }, function(token) {
      console.log('token ' + token);
        if (chrome.runtime.lastError) {
            alert(chrome.runtime.lastError.message);
            return;
        }
        var x = new XMLHttpRequest();
        x.open('GET', 'https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token=' + token);
        x.onload = function() {
          var profile = JSON.parse(x.response);
          console.log('profile ', profile);
          $.post('http://www.sharead.org/auth', {
            'googleid': profile.id,
            'name': profile.name,
            'email': profile.email,
            'access_token': token,
            'service': 'google',
            'image_url': profile.picture
          }, function(response) {
            console.log('response', response);
            localStorage.setItem('sharead-cookie', response.cookie_token);
            console.log('local', localStorage.getItem('sharead-cookie'));
          });
          // alert(x.response);
        };
        x.send();
    });
  }
}
