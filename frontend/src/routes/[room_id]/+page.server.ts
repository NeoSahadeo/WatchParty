import { type Actions } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { connect, _join } from '$lib/connect';

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
		return _join({ request, cookies });
	}
} as Actions;
