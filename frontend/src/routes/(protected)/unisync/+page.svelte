<script lang="ts">
    import { onMount } from "svelte";

    let { data } = $props();
    let { schedule } = $derived(data);

    onMount(() => {
        if (schedule) {
            window.localStorage.setItem(
                "unisync-cached-schedule",
                JSON.stringify(schedule),
            );
        }
    });
</script>

<pre>
{JSON.stringify(schedule, null, 2)}
</pre>
