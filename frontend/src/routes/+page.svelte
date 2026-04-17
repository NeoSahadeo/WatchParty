<script lang="ts">
	import { enhance } from '$app/forms';
	import { resolve } from '$app/paths';

	let { form } = $props();

	let room_id = $state();
	let password = $state();

	$effect(() => {
		if (form) {
			room_id = form?.room_id ?? '';
			password = form?.password ?? '';
			if (form?.allowed && form?.status == 200) {
				console.log(resolve(`/${form.room_id}`));
				window.location.assign(resolve(`/${form.room_id}`));
			}
		}
	});
</script>

<main class="flex h-dvh w-full flex-col items-center justify-center">
	<h1 class="text-4xl font-bold">Watch<span class="text-[var(--spicy-paprika)]">Party</span></h1>
	<p>Party of watchers, perchance?</p>
	<form method="POST" class="flex flex-col gap-2 pt-5" action={`?/join`} use:enhance>
		<input
			type="text"
			name="room_id"
			bind:value={room_id}
			placeholder="Room ID"
			class="input input-neutral"
		/>
		<input
			type="password"
			name="password"
			bind:value={password}
			placeholder="Password"
			class="input input-neutral"
		/>
		<button class="btn bg-[var(--spicy-paprika)]">Join</button>
	</form>
</main>
