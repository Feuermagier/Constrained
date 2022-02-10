import type { Point } from "./primitive";

export type Constraint = PointsMatch | PointFixed | WidthFixed | HeightFixed;

export class PointsMatch {
    first: number;
    second: number;
    firstPoint: RectPoint;
    secondPoint: RectPoint;

    constructor(first: number, second: number, firstPoint: RectPoint, secondPoint: RectPoint) {
        this.first = first;
        this.second = second;
        this.firstPoint = firstPoint;
        this.secondPoint = secondPoint;
    }

    toJSON() {
        return {
            PointsMatch: {
                first: this.first,
                second: this.second,
                firstPoint: this.firstPoint,
                secondPoint: this.secondPoint
            }
        };
    }
}

export class PointFixed {
    rect: number;
    point: RectPoint;
    target: Point;

    constructor(rect: number, point: RectPoint, target: Point) {
        this.rect = rect;
        this.point = point;
        this.target = target;
    }

    toJSON() {
        return {
            PointFixed: {
                rect: this.rect,
                point: this.point,
                target: this.target
            }
        };
    }
}

export class WidthFixed {
    rect: number;
    width: number;

    constructor(rect: number, width: number) {
        this.rect = rect;
        this.width = width;
    }

    toJSON() {
        return {
            WidthFixed: {
                rect: this.rect,
                width: this.width
            }
        };
    }
}

export class HeightFixed {
    rect: number;
    height: number;

    constructor(rect: number, height: number) {
        this.rect = rect;
        this.height = height;
    }

    toJSON() {
        return {
            HeightFixed: {
                rect: this.rect,
                height: this.height
            }
        };
    }
}

export enum RectPoint {
    TopLeft = "TopLeft",
    TopRight = "TopRight",
    BottomLeft = "BottomLeft",
    BottomRight = "BottomRight"
}