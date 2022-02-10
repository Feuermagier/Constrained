<script lang="ts">
import { onMount } from "svelte";

    let canvas;

    onMount(() => {
        const context = canvas.getContext("2d", {});

        context.beginPath();
        context.fillStyle = "#000000";
        context.rect(0, 0, 50, 30);
        context.fill();
    })
</script>

<canvas bind:this={canvas} width={100} height={100} />