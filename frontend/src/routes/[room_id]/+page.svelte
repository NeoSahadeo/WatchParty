<script lang="ts">
	import { enhance } from '$app/forms';
	import { resolve } from '$app/paths';
	import { socket } from '$lib/store.svelte.js';
	import type { PageProps } from './$types';

	let { data, form, params }: PageProps = $props();
	let pingInterval = $state(-1);
	let slug = $state(data.room_id || params.room_id);
	let videoElement = $state<HTMLVideoElement>();
	let video = $state({
		src: undefined,
		timestamp: 0,
		leader: false
	});

	function updateHref() {
		window.location.href = `${resolve('/')}${slug}`;
	}

	$effect(() => {
		if (data.allowed) {
			const ws = new WebSocket(`${socket}/ws`);
			ws.addEventListener('open', () => {
				clearInterval(pingInterval);
				pingInterval = setInterval(() => {
					ws.send(
						JSON.stringify({
							client_id: data.user_id!,
							room_id: data.room_id,
							timestamp: video.timestamp,
							leader: video.leader,
							paused: videoElement?.paused
						})
					);
				}, 1000);
			});

			ws.addEventListener('message', (e) => {
				const data = JSON.parse(e.data);
				if (data.src != video.src) {
					video.src = data.src;
				}
				if (Math.abs(video.timestamp - data.timestamp) > 3) {
					video.timestamp = data.timestamp;
				}
				if (!video.leader) {
					if (data.paused) {
						videoElement?.pause();
					} else {
						videoElement?.play();
					}
				}
			});

			ws.addEventListener('close', () => {
				clearInterval(pingInterval);
			});
		}
	});
</script>

{#if form?.description}
	<p class="error">{form.description}</p>
{/if}

{#if data?.success}
	<p>{data.message}</p>
{/if}

{#if !data.allowed}
	<form method="POST" action="?/join" use:enhance>
		<input name="room_id" bind:value={slug} onchange={() => updateHref()} />
		<input name="password" type="password" placeholder="Password" />
		<button>Submit</button>
	</form>
{/if}

<input type="checkbox" bind:checked={video.leader} />

{#if data?.allowed}
	<video src={video.src} bind:this={videoElement} bind:currentTime={video.timestamp} controls>
		Your browser doesn't support video.
	</video>
{/if}
