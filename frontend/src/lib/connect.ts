import { redirect, type Cookies } from '@sveltejs/kit';
import { server } from '$lib/store.svelte';
import { resolve } from '$app/paths';

export async function connect(
	room_id: string,
	user_id: string,
	password: string,
	cookies: Cookies
) {
	const form = new FormData();
	form.set('room_id', room_id);
	form.set('password', password);
	form.set('client_id', user_id);

	try {
		console.log('connection')
		const res = await fetch(`${server}/connect`, {
			method: 'POST',
			body: form
		});

		if (res.ok) {
			cookies.set(`password`, password.toString(), {
				path: '/',
				httpOnly: true,
				secure: false,
				sameSite: 'lax',
				maxAge: 2592000 // 30 days
			});
			cookies.set(`user_id`, user_id, {
				path: '/',
				httpOnly: true,
				secure: false,
				sameSite: 'lax',
				maxAge: 2592000 // 30 days
			});

			return {
				status: 200,
				room_id: room_id,
				user_id: user_id,
				message: 'Connected',
				success: true,
				allowed: true
			};
		} else {
			return {
				status: 400,
				room_id: room_id,
				password: password
			};
		}
	} catch (error) {
		return {
			status: 500,
			message: 'Error contacting server.',
			success: false,
			allowed: false
		};
	}
}

export async function _join({ request, cookies }) {
	const form_data = await request.formData();
	const room_id = form_data.get('room_id');
	const password = form_data.get('password');
	const user_id = cookies.get('user_id') || crypto.randomUUID();

	if (!room_id || !password) {
		return;
	}
	return await connect(room_id.toString(), user_id, password.toString(), cookies);
}
