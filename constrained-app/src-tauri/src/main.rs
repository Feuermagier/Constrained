#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use std::{sync::Mutex, time::Instant};

use constrained_core::solve::{grad_solver::AdamSolver, Solver};

mod constraint;
mod primitive;

struct ServerState<T: constrained_core::solve::Solver> {
    solver: Option<T>,
    loss: f32,
}

fn main() {
    tauri::Builder::default()
        .manage(Mutex::new(ServerState::<AdamSolver> {
            solver: None,
            loss: 0.0f32,
        }))
        .invoke_handler(tauri::generate_handler![do_solver_steps, init_diagram])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

#[tauri::command]
async fn do_solver_steps(
    server_state: tauri::State<'_, Mutex<ServerState<AdamSolver>>>,
) -> Result<SolverStatus, String> {
    let start = Instant::now();
    let mut server_state = server_state.lock().unwrap();

    let rects = if let Some(solver) = &mut server_state.solver {
        let status = solver.optimize();
        let rects = solver
            .diagram()
            .rects
            .iter()
            .map(primitive::Rect::from)
            .collect();
        server_state.loss = status.loss;
        rects
    } else {
        Vec::new()
    };
    let duration = start.elapsed();
    println!("Solved in {}ms", duration.as_millis());

    Ok(SolverStatus {
        rects,
        loss: server_state.loss,
    })
}

#[tauri::command]
async fn init_diagram(
    server_state: tauri::State<'_, Mutex<ServerState<AdamSolver>>>,
    diagram: Diagram,
    steps_per_optimize: u32,
    target_loss: f32,
) -> Result<(), String> {
    dbg!(target_loss);
    let mut server_state = server_state.lock().unwrap();

    let diagram = constrained_core::Diagram {
        rects: diagram
            .rects
            .into_iter()
            .map(constrained_core::Rect::from)
            .collect(),
        constraints: diagram
            .constraints
            .into_iter()
            .map(constrained_core::Constraint::from)
            .collect(),
    };

    server_state.solver = Some(AdamSolver::new(diagram, steps_per_optimize, target_loss));
    server_state.loss = 0f32;

    Ok(())
}

#[derive(serde::Serialize)]
struct SolverStatus {
    rects: Vec<primitive::Rect>,
    loss: f32,
}

#[derive(serde::Deserialize)]
struct Diagram {
    rects: Vec<primitive::Rect>,
    constraints: Vec<constraint::Constraint>,
}
