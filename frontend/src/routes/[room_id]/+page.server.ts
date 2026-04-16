import { error, fail, type Actions, type Cookies } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { server, socket } from '$lib/store.svelte';

async function connect(room_id: string, user_id: string, password: string, cookies: Cookies) {
	const form = new FormData();
	form.set('room_id', room_id);
	form.set('password', password);
	form.set('client_id', user_id);

	try {
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
		}
	} catch (error) {
		return {
			status: 500,
			message: 'Error contacting server.',
			success: true,
			allowed: true
		};
	}
}

export const load: PageServerLoad = async ({ params, cookies }) => {
	let user_id = cookies.get('user_id') || crypto.randomUUID();
	const password = cookies.get('password');
	if (!password)
		return {
			room_id: params.room_id,
			allowed: false
		};

	return await connect(params.room_id, user_id, password, cookies);
};

export const actions = {
	join: async ({ request, cookies }) => {
		const form_data = await request.formData();
		const room_id = form_data.get('room_id');
		const password = form_data.get('password');
		const user_id = crypto.randomUUID();
		if (!room_id || !password) {
			return;
		}
		return await connect(room_id.toString(), user_id, password.toString(), cookies);
	}
} as Actions;
