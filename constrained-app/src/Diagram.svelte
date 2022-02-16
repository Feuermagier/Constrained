<script lang="ts">
    import { onMount } from "svelte";

    import { currentDiagram } from "./model/diagram";
    import { renderScale } from "./model/options";

    let canvas;
    let context;
    let width = 500;
    let height = 500;

    onMount(() => {
        context = canvas.getContext("2d", {});

        let frame;
        (function renderLoop() {
            render();
            frame = requestAnimationFrame(renderLoop);
        })();
        return () => {
            cancelAnimationFrame(frame);
        };
    });


    function render() {
        if (!context) {
            return;
        }

        if (!currentDiagram.getAndClearRedrawRequired()) {
            return;
        }

        context.clearRect(0, 0, width, height);
        for (const rect of currentDiagram.getDiagram().rects) {
            context.beginPath();
            context.fillStyle = "#000000";
            context.rect(
                rect.topLeft.x * $renderScale,
                rect.topLeft.y * $renderScale,
                rect.width * $renderScale,
                rect.height * $renderScale
            );
            context.fill();
        }
    }
</script>

<div class="diagram-wrapper">
    <canvas bind:this={canvas} width={width} height={height} />
</div>