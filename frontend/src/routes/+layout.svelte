<script lang="ts">
	import "$lib/styles/app.css";
	import { invalidateAll } from "$app/navigation";
	import {
		SessionStore,
		SupaStore,
		UserStore,
	} from "$lib/stores/SupaStore.js";
	import { onMount } from "svelte";
	import { fetchWithAuthBrowser } from "$lib/utils/fetchWithAuth.js";
	import { addToast, ToastStore } from "$lib/stores/ToastStore.js";
	import Toast from "$lib/components/Toast.svelte";
	import { setDevice } from "$lib/stores/DeviceStore.js";
	import Header from "$lib/components/Header.svelte";

	let { data, children } = $props();
	let { supabase, session, user } = $derived(data);

	const handleDevice = () => {
		const device: Device = window.matchMedia("(max-width: 767px)").matches
			? "mobile"
			: "desktop";

		document.documentElement.dataset.device = device;
		setDevice(device);
	};

	onMount(() => {
		const {
			data: { subscription },
		} = supabase.auth.onAuthStateChange((event, newSession) => {
			if (
				newSession?.expires_at !== session?.expires_at ||
				event === "SIGNED_OUT"
			) {
				invalidateAll();
			}

			if (
				newSession &&
				newSession.provider_token &&
				newSession.provider_refresh_token
			) {
				(async () => {
					const response = await fetchWithAuthBrowser("/token", {
						method: "POST",
						headers: {
							"Content-Type": "application/json",
						},
						body: JSON.stringify({
							access_token: newSession.provider_token,
							refresh_token: newSession.provider_refresh_token,
						}),
					});

					if (response.status !== 201) {
						addToast({
							message: "Authentication Failed. Please try again",
							type: "danger",
						});

						supabase.auth.signOut();
					}
				})();
			}
		});

		handleDevice();

		SessionStore.set(session);
		SupaStore.set(supabase);
		UserStore.set(user);

		return () => subscription.unsubscribe();
	});
</script>

<svelte:window onresize={handleDevice} />

<div class={`mobile:hidden`}>
	<Header />

	{@render children()}

	<ul>
		{#each $ToastStore as toast (toast.id)}
			<Toast {toast} />
		{/each}
	</ul>
</div>

<div class={`desktop:hidden h-dvh w-dvw bg-stone-950 grid place-items-center`}>
	<div
		class={`max-w-[80%] flex flex-col items-center p-4 border-2 border-neutral-800 rounded-md`}
	>
		<h1 class={`font-amulya font-bold italic text-3xl`}>UniSync</h1>

		<p class={`text-center tracking-tighter`}>
			Please use a desktop device. Mobile displays are not supported
		</p>
	</div>
</div>
