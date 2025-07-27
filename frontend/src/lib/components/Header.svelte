<script lang="ts">
    import { Button } from "bits-ui";
    import NavigationMenu from "$lib/components/NavigationMenu.svelte";
    import Profile from "$lib/components/Profile.svelte";
    import { onMount } from "svelte";
    import { fly } from "svelte/transition";

    let isMounted: boolean = $state(false);
    onMount(() => {
        isMounted = true;
    });
</script>

{#if isMounted}
    <header
        class={`fixed top-4 h-[50px] w-dvw grid place-items-center px-30 `}
        transition:fly
    >
        <nav
            class={`h-full w-full flex flex-grow justify-between items-center`}
        >
            <Button.Root href={`/`}>
                <h1 class={`font-amulya font-bold italic text-3xl`}>UniSync</h1>
            </Button.Root>

            <div class={`flex gap-4`}>
                <Profile />

                <NavigationMenu />
            </div>
        </nav>
    </header>
{/if}
