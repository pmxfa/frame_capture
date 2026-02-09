import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import cv2
import os
from pathlib import Path


class VideoFrameCapture:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Frame Capturer")
        self.root.geometry("1000x750")

        # Video properties
        self.video_path = None
        self.cap = None
        self.is_playing = False
        self.current_frame = None
        self.frame_count = 0
        self.playback_speed = 1.0  # Normal speed

        # Create frames folder if it doesn't exist
        self.frames_folder = Path("frames")
        self.frames_folder.mkdir(exist_ok=True)

        # Setup UI
        self.setup_ui()

        # Keyboard shortcuts
        self.root.bind("<Left>", lambda e: self.previous_frame())
        self.root.bind("<Right>", lambda e: self.next_frame())
        self.root.bind("<space>", lambda e: self.toggle_play())

    def setup_ui(self):
        # Top frame for controls
        control_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        control_frame.pack_propagate(False)

        # First row of controls
        first_row = tk.Frame(control_frame, bg="#2c3e50")
        first_row.pack(fill=tk.X, pady=(5, 0))

        # Load Video button
        self.load_btn = tk.Button(
            first_row,
            text="Load Video",
            command=self.load_video,
            bg="white",
            fg="black",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=8,
            cursor="hand2"
        )
        self.load_btn.pack(side=tk.LEFT, padx=5)

        # Previous Frame button
        self.prev_frame_btn = tk.Button(
            first_row,
            text="◄ Prev Frame",
            command=self.previous_frame,
            bg="white",
            fg="black",
            font=("Arial", 10, "bold"),
            padx=12,
            pady=8,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.prev_frame_btn.pack(side=tk.LEFT, padx=5)

        # Play/Pause button
        self.play_btn = tk.Button(
            first_row,
            text="▶ Play",
            command=self.toggle_play,
            bg="white",
            fg="black",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.play_btn.pack(side=tk.LEFT, padx=5)

        # Next Frame button
        self.next_frame_btn = tk.Button(
            first_row,
            text="Next Frame ►",
            command=self.next_frame,
            bg="white",
            fg="black",
            font=("Arial", 10, "bold"),
            padx=12,
            pady=8,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.next_frame_btn.pack(side=tk.LEFT, padx=5)

        # Speed controls
        speed_label = tk.Label(
            first_row,
            text="Speed:",
            bg="#2c3e50",
            fg="white",
            font=("Arial", 10, "bold")
        )
        speed_label.pack(side=tk.LEFT, padx=(15, 5))

        # Speed dropdown
        self.speed_var = tk.StringVar(value="1.0x")
        self.speed_dropdown = ttk.Combobox(
            first_row,
            textvariable=self.speed_var,
            values=["0.25x", "0.5x", "0.75x", "1.0x", "1.5x", "2.0x", "3.0x", "4.0x", "6.0x","8.0x"],
            width=8,
            state="readonly"
        )
        self.speed_dropdown.pack(side=tk.LEFT, padx=5)
        self.speed_dropdown.bind("<<ComboboxSelected>>", self.change_speed)

        # Capture button
        self.capture_btn = tk.Button(
            first_row,
            text="📷 Capture",
            command=self.capture_frame,
            bg="white",
            fg="black",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.capture_btn.pack(side=tk.LEFT, padx=(15, 5))

        # Info label
        self.info_label = tk.Label(
            first_row,
            text="No video loaded",
            bg="#2c3e50",
            fg="white",
            font=("Arial", 10)
        )
        self.info_label.pack(side=tk.RIGHT, padx=10)

        # Video canvas
        self.canvas = tk.Canvas(self.root, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Progress frame
        progress_frame = tk.Frame(self.root, bg="#34495e", height=50)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        progress_frame.pack_propagate(False)

        # Progress slider
        self.progress_var = tk.DoubleVar()
        self.progress_slider = tk.Scale(
            progress_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.progress_var,
            command=self.seek_video,
            bg="#34495e",
            fg="white",
            highlightthickness=0,
            troughcolor="#2c3e50",
            state=tk.DISABLED
        )
        self.progress_slider.pack(fill=tk.X, padx=10, pady=10)

        # Frame counter label
        self.frame_label = tk.Label(
            self.root,
            text="Frame: 0 / 0",
            bg="#ecf0f1",
            font=("Arial", 10, "bold")
        )
        self.frame_label.pack(pady=5)

    def load_video(self):
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            # Close previous video if any
            if self.cap is not None:
                self.cap.release()

            self.video_path = file_path
            self.cap = cv2.VideoCapture(file_path)

            if not self.cap.isOpened():
                messagebox.showerror("Error", "Could not open video file")
                return

            # Get video properties
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)

            # Enable controls
            self.play_btn.config(state=tk.NORMAL)
            self.capture_btn.config(state=tk.NORMAL)
            self.prev_frame_btn.config(state=tk.NORMAL)
            self.next_frame_btn.config(state=tk.NORMAL)
            self.progress_slider.config(state=tk.NORMAL, to=self.total_frames-1)

            # Update info
            video_name = os.path.basename(file_path)
            self.info_label.config(text=f"Loaded: {video_name}")

            # Show first frame
            self.show_frame()

    def toggle_play(self):
        if self.cap is None:
            return

        self.is_playing = not self.is_playing

        if self.is_playing:
            self.play_btn.config(text="⏸ Pause", bg="white")
            self.play_video()
        else:
            self.play_btn.config(text="▶ Play", bg="white")

    def play_video(self):
        if not self.is_playing or self.cap is None:
            return

        ret, frame = self.cap.read()

        if ret:
            self.current_frame = frame
            self.frame_count = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))

            # Update display
            self.display_frame(frame)

            # Update progress slider
            self.progress_var.set(self.frame_count)

            # Update frame counter
            self.frame_label.config(text=f"Frame: {self.frame_count} / {self.total_frames}")

            # Schedule next frame with adjusted delay based on playback speed
            delay = int((1000 / self.fps) / self.playback_speed) if self.fps > 0 else 30
            self.root.after(delay, self.play_video)
        else:
            # End of video
            self.is_playing = False
            self.play_btn.config(text="▶ Play", bg="white")
            # Reset to beginning
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def show_frame(self):
        if self.cap is None:
            return

        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame
            self.frame_count = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            self.display_frame(frame)
            self.progress_var.set(self.frame_count)
            self.frame_label.config(text=f"Frame: {self.frame_count} / {self.total_frames}")

    def next_frame(self):
        """Go to next frame"""
        if self.cap is None:
            return

        # Pause if playing
        if self.is_playing:
            self.toggle_play()

        current_pos = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        if current_pos < self.total_frames - 1:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, current_pos)
            self.show_frame()

    def previous_frame(self):
        """Go to previous frame"""
        if self.cap is None:
            return

        # Pause if playing
        if self.is_playing:
            self.toggle_play()

        current_pos = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        if current_pos > 1:
            # Go back 2 frames because show_frame will advance by 1
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, current_pos - 2)
            self.show_frame()

    def change_speed(self, event=None):
        """Change playback speed"""
        speed_text = self.speed_var.get()
        self.playback_speed = float(speed_text.replace('x', ''))

    def display_frame(self, frame):
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Resize frame to fit canvas while maintaining aspect ratio
        if canvas_width > 1 and canvas_height > 1:
            h, w = frame_rgb.shape[:2]
            aspect = w / h

            if canvas_width / canvas_height > aspect:
                new_height = canvas_height
                new_width = int(canvas_height * aspect)
            else:
                new_width = canvas_width
                new_height = int(canvas_width / aspect)

            frame_resized = cv2.resize(frame_rgb, (new_width, new_height))

            # Convert to PIL Image and then to ImageTk
            img = Image.fromarray(frame_resized)
            self.photo = ImageTk.PhotoImage(image=img)

            # Update canvas
            self.canvas.delete("all")
            self.canvas.create_image(
                canvas_width // 2,
                canvas_height // 2,
                image=self.photo,
                anchor=tk.CENTER
            )

    def seek_video(self, value):
        if self.cap is None or self.is_playing:
            return

        frame_number = int(float(value))
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        self.show_frame()

    def capture_frame(self):
        if self.current_frame is None:
            messagebox.showwarning("Warning", "No frame to capture")
            return

        # Get video title (filename without extension)
        video_title = Path(self.video_path).stem if self.video_path else "unknown"

        # Find next available filename with new naming pattern
        pattern = f"{video_title}_*.jpg"
        existing_files = list(self.frames_folder.glob(pattern))
        if existing_files:
            # Extract numbers from filenames
            numbers = []
            for f in existing_files:
                try:
                    # Get the last part after the last underscore
                    num = int(f.stem.split('_')[-1])
                    numbers.append(num)
                except:
                    pass
            next_num = max(numbers) + 1 if numbers else 1
        else:
            next_num = 1

        # Save frame with new naming: {video_title}_{frame_number}
        filename = self.frames_folder / f"{video_title}_{next_num:04d}.jpg"
        cv2.imwrite(str(filename), self.current_frame)

        # Show confirmation
        self.info_label.config(text=f"Saved: {filename.name}")
        # messagebox.showinfo("Success", f"Frame saved as {filename.name}")

    def __del__(self):
        if self.cap is not None:
            self.cap.release()


def main():
    root = tk.Tk()
    app = VideoFrameCapture(root)
    root.mainloop()


if __name__ == "__main__":
    main()