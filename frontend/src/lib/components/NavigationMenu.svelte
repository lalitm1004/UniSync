<script lang="ts">
    import { page } from "$app/state";
    import { Button, DropdownMenu } from "bits-ui";
    import { slide } from "svelte/transition";

    const internalAnchors = [
        {
            display: "Home",
            href: "/",
            icon: houseSvg,
        },
        {
            display: "UniSync",
            href: "/unisync",
            icon: calendarSyncSvg,
        },
        {
            display: "Guide",
            href: "/guide",
            icon: infoSvg,
        },
    ];

    const menuText = $derived.by(() => {
        const pathname = page.url.pathname;
        const filtered = internalAnchors.filter(
            (a) =>
                a.href === pathname ||
                a.href.startsWith(`${page.url.pathname}/`),
        );
        return filtered[0]?.display || "404";
    });
</script>

<DropdownMenu.Root>
    <DropdownMenu.Trigger
        class={`h-[40px] w-[144px] flex justify-between items-center pl-3 pr-2 py-1.5 bg-stone-950 hover:bg-stone-800/80 border-2 border-neutral-800 rounded-md cursor-pointer transition-colors duration-300`}
    >
        <p>{menuText}</p>

        {@render upDownSvg()}
    </DropdownMenu.Trigger>

    <DropdownMenu.Portal>
        <DropdownMenu.Content
            class={`w-[144px] py-2 bg-stone-950 border-2 border-neutral-800 rounded-md`}
            sideOffset={8}
            forceMount
        >
            {#snippet child({ wrapperProps, props, open })}
                {#if open}
                    <div {...wrapperProps}>
                        <div {...props} transition:slide>
                            <DropdownMenu.Group class={`flex flex-col gap-1`}>
                                {#each internalAnchors as anchor, idx (idx)}
                                    {@const href = anchor.href}
                                    {@const pathname = page.url.pathname}

                                    <DropdownMenu.Item class={`group`}>
                                        <Button.Root
                                            {href}
                                            data-current={pathname === href ||
                                                pathname.startsWith(`${href}/`)}
                                            class={`flex items-center justify-between mx-2 px-2 py-1 data-[current="true"]:bg-neutral-800/50 data-[current="false"]:group-hover:bg-neutral-800/50 rounded-md outline-0 transition-colors duration-300`}
                                        >
                                            <p>{anchor.display}</p>

                                            {@render anchor.icon()}
                                        </Button.Root>
                                    </DropdownMenu.Item>
                                {/each}
                            </DropdownMenu.Group>
                        </div>
                    </div>
                {/if}
            {/snippet}
        </DropdownMenu.Content>
    </DropdownMenu.Portal>
</DropdownMenu.Root>

{#snippet upDownSvg()}
    <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="h-[20px] aspect-square fill-none stroke-2 stroke-neutral-300 lucide lucide-chevrons-up-down-icon lucide-chevrons-up-down"
    >
        <path d="m7 15 5 5 5-5" />
        <path d="m7 9 5-5 5 5" />
    </svg>
{/snippet}

{#snippet houseSvg()}
    <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="h-[20px] aspect-square fill-none stroke-2 stroke-neutral-300 lucide lucide-house-icon lucide-house"
    >
        <path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8" />
        <path
            d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"
        />
    </svg>
{/snippet}

{#snippet calendarSyncSvg()}
    <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="h-[20px] aspect-square fill-none stroke-2 stroke-neutral-300 lucide lucide-calendar-sync-icon lucide-calendar-sync"
    >
        <path d="M11 10v4h4" />
        <path d="m11 14 1.535-1.605a5 5 0 0 1 8 1.5" />
        <path d="M16 2v4" />
        <path d="m21 18-1.535 1.605a5 5 0 0 1-8-1.5" />
        <path d="M21 22v-4h-4" />
        <path
            d="M21 8.5V6a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h4.3"
        />
        <path d="M3 10h4" /><path d="M8 2v4" />
    </svg>
{/snippet}

{#snippet infoSvg()}
    <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="h-[20px] aspect-square fill-none stroke-2 stroke-neutral-300 lucide lucide-info-icon lucide-info"
    >
        <circle cx="12" cy="12" r="10" /><path d="M12 16v-4" />
        <path d="M12 8h.01" />
    </svg>
{/snippet}
