<script lang="ts">
	import { enhance } from '$app/forms';
	import { resolve } from '$app/paths';
	import { socket } from '$lib/store.svelte.js';
	import { onMount } from 'svelte';
	import type { PageProps } from './$types';

	let { data, form, params }: PageProps = $props();
	let pingInterval = $state(-1);

	let videosModal = $state<HTMLDialogElement>();
	let videoFiles = $state({
		files: [],
		display: []
	});
	let videoFilesRequest = $state(false);
	let videoFilesSearch = $state('');

	let leaderModal = $state<HTMLDialogElement>();
	let videoLoaded = $state(true);
	let closeLeaderModal = $state<HTMLButtonElement>();
	let socket_instance = $state<Socket>();

	let slug = $state(data.room_id || params.room_id);
	let videoElement = $state<HTMLVideoElement>();
	let video = $state({
		src: '',
		timestamp: 0,
		leader: false,
		paused: true
	});

	onMount(() => {
		document.body.style.overflow = 'hidden';
	});

	$effect(() => {
		if (!videoLoaded) {
			document.body.style.overflow = 'hidden';
		} else {
			document.body.style.overflow = '';
		}
	});

	$effect(() => {
		videoFiles.display = videoFiles.files.filter((e: string) =>
			e.toLowerCase().includes(videoFilesSearch.toLowerCase())
		);
	});

	class Socket {
		private static instance: Socket;
		ws: WebSocket;

		private constructor() {
			this.ws = new WebSocket(`${socket()}/ws`);

			this.ws.addEventListener('open', () => {
				clearInterval(pingInterval);
				pingInterval = setInterval(() => {
					this.ws.send(
						JSON.stringify({
							type: 'sync',
							client_id: data.user_id!,
							room_id: data.room_id,
							timestamp: video.timestamp,
							leader: video.leader
						})
					);
				}, 1000);
			});

			this.ws.addEventListener('message', (e) => {
				const data = JSON.parse(e.data);

				if (data.src && data.src != video.src) {
					video.src = `http://${window.location.hostname}:8000${data.src}`;
				}

				if (Math.abs(video.timestamp - data.timestamp) > 3) {
					video.timestamp = data.timestamp;
				}

				if (data.paused === true) {
					videoElement?.pause();
				} else if (data.paused === false) {
					videoElement?.play();
				}

				if (data.video_files) {
					videoFiles.files = data.video_files;
					videoFiles.display = data.video_files;
					videoFilesRequest = false;
				}
			});

			this.ws.addEventListener('close', () => {
				clearInterval(pingInterval);
			});
		}

		static getInstance(): Socket {
			if (!Socket.instance) {
				Socket.instance = new Socket();
			}
			return Socket.instance;
		}

		send(data: string | ArrayBufferLike | Blob | ArrayBufferView): void {
			this.ws.send(data);
		}
	}

	$effect(() => {
		if (data.allowed) {
			socket_instance = Socket.getInstance();

			const _reqsrc = () => {
				socket_instance!.send(
					JSON.stringify({
						type: 'command',
						command: 'request src',
						client_id: data.user_id!,
						room_id: data.room_id
					})
				);
				socket_instance!.ws.removeEventListener('open', _reqsrc);
			};
			socket_instance.ws.addEventListener('open', _reqsrc);
		}
	});
</script>

{#if !data.allowed}
	<main class="flex h-dvh w-full flex-col items-center justify-center">
		<a href={resolve('/')}>
			<h1 class="text-4xl font-bold">
				Watch<span class="text-[var(--spicy-paprika)]">Party</span>
			</h1>
			<p>Party of watchers, perchance?</p>
		</a>
		<form method="POST" class="flex flex-col gap-2 pt-5" action={`?/join`} use:enhance>
			<div role="alert" class="alert alert-info max-w-xs">
				<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
					><g
						fill="none"
						stroke="currentColor"
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"><circle cx="12" cy="12" r="10" /><path d="M12 16v-4m0-4h.01" /></g
					></svg
				>
				<p>Password required to join the server.</p>
			</div>
			<input
				type="text"
				name="room_id"
				bind:value={slug}
				placeholder="Room ID"
				class="input input-neutral"
			/>
			<input type="password" name="password" placeholder="Password" class="input input-neutral" />
			<button class="btn bg-[var(--spicy-paprika)]">Join</button>
		</form>
	</main>
{/if}

<dialog bind:this={leaderModal} class="modal">
	<div class="modal-box">
		<h3 class="text-lg font-bold">
			Confirm: You want to {video.leader ? 'stop being' : 'become'} the leader.
		</h3>
		<ol class="list-decimal px-8">
			<li>There can only be ONE group leader.</li>
			<li>Make sure that the video is paused.</li>
			<li>The current leader must turn off group leader.</li>
			<li>If there is no group leader the video will not play.</li>
		</ol>
		<div class="modal-action pt-4">
			<button
				class="btn btn-primary"
				onclick={(e) => {
					e.preventDefault();
					e.stopImmediatePropagation();
					video.leader = !video.leader;
					closeLeaderModal?.click();
				}}
			>
				Confirm, {video.leader ? 'stop being leader' : 'make me leader'}
			</button>
			<form method="dialog">
				<button class="btn" bind:this={closeLeaderModal}>Cancel</button>
			</form>
		</div>
	</div>
</dialog>

<dialog bind:this={videosModal} class="modal">
	<div class="modal-box relative">
		<h3 class="text-lg font-bold">Available videos:</h3>
		{#if videoFilesRequest}
			<div class="ml-auto mr-auto mt-8 w-fit">
				<span class="loading loading-ring loading-xl"></span>
				<span class="loading loading-ring loading-xl"></span>
				<span class="loading loading-ring loading-xl"></span>
				<span class="loading loading-ring loading-xl"></span>
				<span class="loading loading-ring loading-xl"></span>
			</div>
		{:else}
			<label class="input mt-4">
				<svg class="h-[1em] opacity-50" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
					<g
						stroke-linejoin="round"
						stroke-linecap="round"
						stroke-width="2.5"
						fill="none"
						stroke="currentColor"
					>
						<circle cx="11" cy="11" r="8"></circle>
						<path d="m21 21-4.3-4.3"></path>
					</g>
				</svg>
				<input bind:value={videoFilesSearch} type="search" placeholder="Search" />
			</label>
			<div class="flex flex-col gap-2 px-3 pt-3 max-h-50 overflow-scroll mb-10">
				{#each videoFiles.display as file}
					<button
						onclick={() => {
							socket_instance?.send(
								JSON.stringify({
									type: 'command',
									command: 'load video',
									data: file,
									client_id: data.user_id!,
									room_id: data.room_id
								})
							);
						}}
						class="min-h-10 max-w-10 bg-base-200 rounded-full hover:bg-primary hover:cursor-pointer max-w-xs overflow-ellipsis px-3 overflow-hidden truncate text-left"
						>{file}</button
					>
				{/each}
			</div>
		{/if}
		<div class="modal-action pb-4 pr-4 fixed right-0 bottom-0">
			<form method="dialog">
				<button class="btn">Close</button>
			</form>
		</div>
	</div>
</dialog>

{#if data?.allowed}
	{#if !videoLoaded}
		<div class="w-full h-[100dvh] flex flex-col items-center justify-center">
			<div class="text-2xl font-bold pb-5">Loading the Video</div>
			<div>
				<span class="loading loading-ring loading-xl"></span>
				<span class="loading loading-ring loading-xl"></span>
				<span class="loading loading-ring loading-xl"></span>
				<span class="loading loading-ring loading-xl"></span>
				<span class="loading loading-ring loading-xl"></span>
			</div>
		</div>
	{/if}
	<main class="min-h-[100dvh]">
		<video
			oncanplay={() => (videoLoaded = true)}
			src={video.src}
			bind:this={videoElement}
			bind:currentTime={video.timestamp}
			onplay={() => {
				if (video.leader) {
					if (!socket_instance) return;
					socket_instance.send(
						JSON.stringify({
							type: 'command',
							command: 'play'
						})
					);
				}
			}}
			onpause={() => {
				if (video.leader) {
					if (!socket_instance) return;
					socket_instance.send(
						JSON.stringify({
							type: 'command',
							command: 'pause'
						})
					);
				}
			}}
			controls
			class="w-full"
			bind:paused={video.paused}
			muted={true}
		>
			Your browser doesn't support video.
			<track kind="captions" />
		</video>
		{#if videoElement}
			<div class="mt-3 mx-3 px-4 bg-base-100 w-fit py-2 card">
				<h6 class="font-bold">Group Controls</h6>
				<div class="pl-4 pt-2">
					<button
						class="btn btn-primary"
						onclick={() => {
							if (video.paused) {
								videoElement!.play();
								if (!socket_instance) return;
								socket_instance.send(
									JSON.stringify({
										type: 'command',
										command: 'play'
									})
								);
							} else {
								videoElement!.pause();
								if (!socket_instance) return;
								socket_instance.send(
									JSON.stringify({
										type: 'command',
										command: 'pause'
									})
								);
							}
						}}
					>
						{#if video.paused}
							<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
								><path
									fill="currentColor"
									d="M6.51 18.87c.15.09.32.13.49.13s.36-.05.51-.14l10-6c.3-.18.49-.51.49-.86s-.18-.68-.49-.86l-10-6a.99.99 0 0 0-1.01-.01c-.31.18-.51.51-.51.87v12c0 .36.19.69.51.87Z"
								/></svg
							>
						{:else}
							<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
								><path
									fill="currentColor"
									d="M16 19q-.825 0-1.412-.587T14 17V7q0-.825.588-1.412T16 5t1.413.588T18 7v10q0 .825-.587 1.413T16 19m-8 0q-.825 0-1.412-.587T6 17V7q0-.825.588-1.412T8 5t1.413.588T10 7v10q0 .825-.587 1.413T8 19"
								/></svg
							>
						{/if}
					</button>
				</div>
			</div>
		{/if}
		<div class="bg-base-100 w-full max-w-xs px-3 py-4 shadow-xl card mx-3 mt-3">
			<h6 class="font-bold">Options:</h6>
			<div class="pl-4 flex flex-col gap-4">
				<div>
					<span> Group Leader </span>
					<input
						type="checkbox"
						onclick={(e) => {
							e.preventDefault();
							e.stopImmediatePropagation();
							leaderModal!.showModal();
						}}
						bind:checked={video.leader}
						class="toggle toggle-xl toggle-primary"
					/>
				</div>
				<div>
					<button
						onclick={() => {
							videosModal!.showModal();
							videoFilesRequest = true;
							socket_instance?.send(
								JSON.stringify({
									type: 'command',
									command: 'request video files'
								})
							);
						}}
						class="btn btn-info"
						disabled={!video.leader}>View Videos</button
					>
				</div>
			</div>
		</div>
	</main>
{/if}
