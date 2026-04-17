import { type Actions } from '@sveltejs/kit';
import { connect, _join } from '$lib/connect';

export const actions = {
	join: async ({ request, cookies }) => {
		return _join({ request, cookies });
	}
} as Actions;
