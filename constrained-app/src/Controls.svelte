<script lang="ts">
    import { renderScale } from "./model/options";
</script>

<div class="controls">
    <input
        type="range"
        min="0.1"
        max="200.0"
        bind:value={$renderScale}
        id="renderScaleInput"
    />
</div>

<style>
    .controls {
        display: flex;
        flex-flow: column;
    }

    input[type="slider"] {
    }
</style>
