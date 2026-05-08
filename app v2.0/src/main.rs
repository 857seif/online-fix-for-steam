#![windows_subsystem = "windows"]
use eframe::egui;
use rfd::FileDialog;
use std::fs::{self, File};
use std::io::Write;
use std::path::{PathBuf};
use std::sync::mpsc::{self, Receiver, Sender};
use std::thread;
use walkdir::WalkDir;

const RAW_BASE: &str = "https://raw.githubusercontent.com/857seif/online-fix-for-steam/main/";

struct AfandiLauncher {
    game_path: String,
    app_id: String,
    enable_overlay: bool,
    status: String,
    is_installing: bool,
    receiver: Receiver<String>,
    sender: Sender<String>,
}

impl Default for AfandiLauncher {
    fn default() -> Self {
        let (sender, receiver) = mpsc::channel();
        Self {
            game_path: String::new(),
            app_id: String::new(),
            enable_overlay: true,
            status: "Ready...".to_string(),
            is_installing: false,
            sender,
            receiver,
        }
    }
}

impl AfandiLauncher {
    fn find_locations(start_dir: &str) -> (Option<PathBuf>, Option<bool>, Option<PathBuf>) {
        let mut api_dir = None;
        let mut is_64 = None;
        let mut exe_dir = None;
        for entry in WalkDir::new(start_dir).into_iter().filter_map(|e| e.ok()) {
            let path = entry.path();
            let file_name = path.file_name().and_then(|n| n.to_str()).unwrap_or("");
            if file_name == "steam_api64.dll" {
                api_dir = Some(path.parent().unwrap().to_path_buf());
                is_64 = Some(true);
            } else if file_name == "steam_api.dll" {
                api_dir = Some(path.parent().unwrap().to_path_buf());
                is_64 = Some(false);
            }
            if file_name.to_lowercase().ends_with(".exe") {
                let lower_name = file_name.to_lowercase();
                if !["crash", "launcher", "unity"].iter().any(|&x| lower_name.contains(x)) {
                    exe_dir = Some(path.parent().unwrap().to_path_buf());
                }
            }
        }
        (api_dir, is_64, exe_dir)
    }

    fn run_install(game_path: String, app_id: String, overlay: bool, sender: Sender<String>) {
        let (api_dir, is_64, exe_dir) = Self::find_locations(&game_path);
        if api_dir.is_none() || exe_dir.is_none() {
            let _ = sender.send("Error: Game files not found!".to_string());
            return;
        }
        let (api_dir, exe_dir, is_64) = (api_dir.unwrap(), exe_dir.unwrap(), is_64.unwrap());
        let branch = if is_64 { "x64" } else { "x32" };
        let mut files = vec!["version.dll", "afandi.ini"];
        if overlay { files.push("SteamOverlay64.dll"); }
        files.push(if is_64 { "Afandi%20online%20fix-64.dll" } else { "Afandi%20online%20fix-32.dll" });

        let client = reqwest::blocking::Client::new();
        for f in files {
            let _ = sender.send(format!("Downloading {}...", f.replace("%20", " ")));
            if let Ok(res) = client.get(format!("{}{}/{}", RAW_BASE, branch, f)).send().and_then(|r| r.bytes()) {
                let mut file = File::create(exe_dir.join(f.replace("%20", " "))).unwrap();
                let _ = file.write_all(&res).unwrap();
            }
        }
        let api_name = if is_64 { "steam_api64.dll" } else { "steam_api.dll" };
        if let Ok(res) = client.get(format!("{}{}/{}", RAW_BASE, branch, api_name)).send().and_then(|r| r.bytes()) {
            let mut file = File::create(api_dir.join(api_name)).unwrap();
            let _ = file.write_all(&res).unwrap();
        }
        let ini = format!("[Settings]\nAppId=480\nogAppId={}\nPluginsFolder=plugins\n", app_id);
        let _ = fs::write(exe_dir.join("afandi.ini"), ini);
        let _ = sender.send("Installation Successful! ✅".to_string());
    }
}

impl eframe::App for AfandiLauncher {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        if let Ok(msg) = self.receiver.try_recv() {
            self.status = msg;
            if self.status.contains("Successful") || self.status.contains("Error") { self.is_installing = false; }
        }
        egui::CentralPanel::default().show(ctx, |ui| {
            ui.vertical_centered(|ui| {
                ui.heading(egui::RichText::new("AFANDI ONLINE FIX").size(24.0).strong().color(egui::Color32::from_rgb(59, 142, 208)));
            });
            ui.add_space(20.0);
            ui.horizontal(|ui| {
                ui.label("Game Path:");
                ui.text_edit_singleline(&mut self.game_path);
                if ui.button("BROWSE").clicked() {
                    if let Some(path) = FileDialog::new().pick_folder() { self.game_path = path.display().to_string(); }
                }
            });
            ui.add_space(10.0);
            ui.horizontal(|ui| {
                ui.label("Original AppID:");
                ui.text_edit_singleline(&mut self.app_id);
            });
            ui.checkbox(&mut self.enable_overlay, "Enable Steam Overlay");
            ui.add_space(20.0);
            ui.vertical_centered(|ui| {
                if self.is_installing { 
                    // Fixed: used .animate(true) instead of .animated(true)
                    ui.add(egui::ProgressBar::new(0.5).animate(true)); 
                }
                else if ui.add_sized([200.0, 40.0], egui::Button::new("INSTALL FIX")).clicked() {
                    if !self.game_path.is_empty() && !self.app_id.is_empty() {
                        self.is_installing = true;
                        let (s, p, id, ov) = (self.sender.clone(), self.game_path.clone(), self.app_id.clone(), self.enable_overlay);
                        thread::spawn(move || { AfandiLauncher::run_install(p, id, ov, s); });
                    }
                }
                ui.add_space(10.0);
                ui.label(&self.status);
            });
        });
    }
}

fn main() -> Result<(), eframe::Error> {
    let options = eframe::NativeOptions { initial_window_size: Some(egui::vec2(500.0, 400.0)), ..Default::default() };
    eframe::run_native("Afandi Launcher", options, Box::new(|_| Box::new(AfandiLauncher::default())))
}