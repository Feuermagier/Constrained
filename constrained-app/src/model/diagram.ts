import { invoke } from "@tauri-apps/api/tauri";
import { Constraint, HeightFixed, PointFixed, PointsMatch, RectPoint, WidthFixed } from "./constraint";
import { Point, Rect } from "./primitive";

export class Diagram {
    rects: Rect[];
    constraints: Constraint[]

    constructor(rects: Rect[], constraints: Constraint[]) {
        this.rects = rects;
        this.constraints = constraints;
    }
}

export class CurrentDiagram {
    private diagram: Diagram;
    private redrawRequired: boolean;

    constructor(diagram: Diagram, stepsPerCall: number, targetLoss: number) {
        this.redrawRequired = true;
        this.diagram = diagram;
        invoke("init_diagram", {
            diagram: diagram,
            stepsPerOptimize: stepsPerCall,
            targetLoss: targetLoss
        });
    }

    /** 
     * NEVER modify the returned diagram, as listeners will not get notified.
    */
    getDiagram(): Diagram {
        return this.diagram;
    }

    doSolverSteps() {
        invoke("do_solver_steps", {}).then(s => {
            let status = s as SolverStatus;
            this.diagram.rects = status.rects;
            this.redrawRequired = true;
        });
    }

    getAndClearRedrawRequired(): boolean {
        let required = this.redrawRequired;
        this.redrawRequired = false;
        return required;
    }
}

class SolverStatus {
    rects: Rect[];
    loss: number;
}

export const currentDiagram = new CurrentDiagram(new Diagram(
    [
        new Rect(new Point(0, 0), 1, 1),
        new Rect(new Point(0, 0), 1, 1)],
    [
        new PointsMatch(0, 1, RectPoint.BottomRight, RectPoint.TopLeft),
        new PointFixed(0, RectPoint.TopLeft, new Point(0, 0)),
        new WidthFixed(0, 1),
        new HeightFixed(0, 1)
    ]
), 10, 0.001);