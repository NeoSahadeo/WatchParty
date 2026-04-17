import { PUBLIC_IP, PUBLIC_LOCAL_IP } from '$env/static/public';

export const server = $state(`http://${PUBLIC_LOCAL_IP}:8000`);

export const socket = $state(() => {
	// If on same network as server (10.10.10.x), use internal
	if (
		window.location.hostname === 'localhost' ||
		window.location.hostname.startsWith(PUBLIC_LOCAL_IP.split('.').slice(0, -1).join('.'))
	) {
		return `ws://${PUBLIC_LOCAL_IP}:8000`;
	}
	console.log(window.location.hostname);
	// External: use public IP/domain + external port
	return `ws://${PUBLIC_IP}:8000`;
});
