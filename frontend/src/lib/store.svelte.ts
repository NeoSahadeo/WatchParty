export const server = $state('http://10.10.10.172:8000');
// export const socket = $state('ws://10.10.10.172:8000');
export const socket = $state(() => {
	// If on same network as server (10.10.10.x), use internal
	if (
		window.location.hostname === 'localhost' ||
		window.location.hostname.startsWith('10.10.10.')
	) {
		return 'ws://10.10.10.172:8000';
	}
	// External: use public IP/domain + external port
	return 'ws://196.216.137.220:8000'; // Or your domain
});
