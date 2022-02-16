<script lang="ts">
	import Controls from "./Controls.svelte";
	import Diagram from "./Diagram.svelte";
	import { currentDiagram } from "./model/diagram";

	//let solverInterval = setInterval(() => currentDiagram.doSolverSteps(50), 30);
	//currentDiagram.doSolverSteps(100)
	doSolverSteps();

	function doSolverSteps() {
		currentDiagram.doSolverSteps();
		setTimeout(doSolverSteps, 30);
	}
</script>

<main>
	<div class="diagram">
		<Diagram />
	</div>
	<div class="controls">
		<Controls />
	</div>
</main>

<style>
	main {
		width: 100%;
		height: 100%;
		display: flex;
		flex-flow: row;
	}

	.diagram {
		flex-grow: 1;
		overflow: auto;
	}

	.controls {
		min-width: 200px;
	}
</style>
