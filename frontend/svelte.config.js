import adapter from '@sveltejs/adapter-node';
import { config as dotenvConfig } from 'dotenv';

dotenvConfig();

/** @type {import('@sveltejs/kit').Config} */
const config = {
	compilerOptions: {
		// Force runes mode for the project, except for libraries. Can be removed in svelte 6.
		runes: ({ filename }) => (filename.split(/[/\\]/).includes('node_modules') ? undefined : true)
	},
	kit: {
		adapter: adapter(),
		csrf: {
			trustedOrigins: [
				'http://localhost:5173',
				`http://${process.env.PUBLIC_LOCAL_IP}:4173`,
				`http://${process.env.PUBLIC_IP}:4173`
			]
		}
	}
};

export default config;
