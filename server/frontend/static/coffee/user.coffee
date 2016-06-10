window.user  = {
	authorize_google: (googleid, name, email, access_token) ->
		$.post('auth', {
				'googleid': googleid,
				'name': name,
				'email': email,
				'access_token': access_token,
				'service': 'google'
			}, (response) ->);
}