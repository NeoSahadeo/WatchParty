// import type { HandleFetch } from '@sveltejs/kit';
//
// export const handleFetch: HandleFetch = async ({ event, request, fetch }) => {
// 	const userId = event.cookies.get('user_id');
// 	// event.cookies.get("password")
//
// 	if (userId) {
// 		console.log('setting headers');
//
// 		const newRequest = new Request(request, {
// 			headers: new Headers(request.headers)
// 		});
// 		newRequest.headers.set('x-user-id', userId);
//
// 		return fetch(newRequest);
// 	}
//
// 	return fetch(request);
// };
