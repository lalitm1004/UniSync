<script lang="ts">
    import { Button } from "bits-ui";
    import NavigationMenu from "$lib/components/NavigationMenu.svelte";
</script>

<header class={`fixed top-4 h-[50px] w-dvw grid place-items-center px-30 `}>
    <nav class={`h-full w-full flex flex-grow justify-between items-center`}>
        <Button.Root href={`/`}>
            <h1 class={`font-amulya font-bold italic text-3xl`}>UniSync</h1>
        </Button.Root>

        <NavigationMenu />
    </nav>
</header>
