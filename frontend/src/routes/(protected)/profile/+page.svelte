<script lang="ts">
    import { Button } from "bits-ui";
    import { onMount } from "svelte";
    import { fly } from "svelte/transition";

    let { data } = $props();
    let { supabase, user } = $derived(data);

    const handleSignOut = () => {
        supabase.auth.signOut();
    };

    let isMounted: boolean = $state(false);
    onMount(() => {
        isMounted = true;
    });
</script>

{#if isMounted}
    <main class={`h-dvh w-dvw grid place-items-center`} transition:fly>
        {#if user}
            <div
                class={`flex flex-col items-center px-10 py-4 gap-2 border-2 border-neutral-800 rounded-md`}
            >
                <div class={`text-center`}>
                    <p class={`font-semibold`}>Signed In as:</p>

                    <p>{user.email}</p>
                </div>

                <Button.Root
                    onclick={handleSignOut}
                    class={` px-4 py-2 hover:bg-red-500/40 border-2 border-red-800 rounded-md cursor-pointer transition-colors duration-300`}
                >
                    Sign Out
                </Button.Root>
            </div>
        {/if}
    </main>
{/if}
