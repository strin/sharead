window.user  = {
	authorize_google: (googleid, name, email, access_token, image_url, callback) ->
		$.post('auth', {
				'googleid': googleid,
				'name': name,
				'email': email,
				'access_token': access_token,
				'service': 'google',
				'image_url': image_url
			}, (response) -> 
				console.log('response', response);
				callback()
			);
}