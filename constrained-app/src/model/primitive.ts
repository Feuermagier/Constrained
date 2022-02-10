export class Point {
    readonly x;
    readonly y;

    constructor(x: number, y: number) {
        this.x = x;
        this.y = y;
    }
}

export class Rect {
    readonly topLeft: Point;
    readonly width: number;
    readonly height: number;

    constructor(topLeft: Point, width: number, height: number) {
        this.topLeft = topLeft;
        this.height = height;
        this.width = width;
    }
}