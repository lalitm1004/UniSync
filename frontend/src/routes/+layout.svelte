<script lang="ts">
	import { invalidateAll } from "$app/navigation";
	import {
		SessionStore,
		SupaStore,
		UserStore,
	} from "$lib/stores/SupaStore.js";
	import { onMount } from "svelte";
	import "$lib/styles/app.css";
	import { fetchWithAuthBrowser } from "$lib/utils/fetchWithAuth.js";
	import { addToast, ToastStore } from "$lib/stores/ToastStore.js";
	import Toast from "$lib/components/Toast.svelte";

	let { data, children } = $props();
	let { supabase, session, user } = $derived(data);

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
						invalidateAll();
					}
				})();
			}
		});

		SessionStore.set(session);
		SupaStore.set(supabase);
		UserStore.set(user);

		addToast({
			message: "sex",
			type: "danger",
		});

		return () => subscription.unsubscribe();
	});
</script>

{@render children()}

<ul>
	{#each $ToastStore as toast (toast.id)}
		<Toast {toast} />
	{/each}
</ul>
