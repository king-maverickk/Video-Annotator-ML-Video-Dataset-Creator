import tkinter as tk
from tkinter import filedialog
import vlc, random, os, threading, keyboard
from moviepy.video.io.VideoFileClip import VideoFileClip


class VideoCutter:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Cutter")
        self.root.geometry("+0+0")
        self.loop_buttons_frame = tk.Frame(self.root)
        self.loop_buttons_frame.pack(padx=10, pady=10)

        self.muted = False  # Flag to track mute state

        self.media_player = None
        self.duration = 0
        self.loop_markers = {}  # Dictionary to store the loop markers
        self.time_ranges = []

        # keyboard.on_press(self.spacePause) # new
        keyboard.on_press(self.handle_key_press) # new

        self.create_ui()

        self.media_player.set_xwindow(self.root.winfo_id()) # new
        self.root.protocol("WM_DELETE_WINDOW", self.release) # new

    def create_ui(self):
        # Creating the video player component
        self.instance = vlc.Instance()
        self.media_player = self.instance.media_player_new()

        # Creating the video player window
        self.video_frame = tk.Frame(self.root)
        self.video_frame.place(x=430, y=0)  
        self.video_frame.pack(pady=10)  

        # Creating the control buttons
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(pady=10)

        self.play_button = tk.Button(self.control_frame, text="Play", command=self.play)
        self.play_button.grid(row=0, column=0, padx=5)

        self.pause_button = tk.Button(self.control_frame, text="Pause", command=self.pause)
        self.pause_button.grid(row=0, column=1, padx=5)

        self.rewind_button = tk.Button(self.control_frame, text="Rewind", command=self.rewind)
        self.rewind_button.grid(row=0, column=2, padx=5)

        self.forward_button = tk.Button(self.control_frame, text="Forward", command=self.fast_forward_frames)
        self.forward_button.grid(row=0, column=3, padx=5)

        # Create a mute button
        self.mute_button = tk.Button(self.root, text="Mute", command=self.toggle_mute)
        self.mute_button.pack(padx=10, pady=5)

        # new
        # Create undo button
        self.undo_button = tk.Button(self.root, text="Undo", command=self.undo)
        self.undo_button.pack(padx=10)

        # Creating the seekbar control
        self.seekbar = tk.Scale(
            self.control_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            length=400,
            showvalue=False,
            command=self.update_seek
        )
        self.seekbar.grid(row=1, columnspan=4, pady=10)

        # Creating the timestamps
        self.timestamp_frame = tk.Frame(self.root)
        self.timestamp_frame.pack()

        self.current_time_label = tk.Label(self.timestamp_frame, text="00:00")
        self.current_time_label.grid(row=0, column=0, padx=5)

        self.total_time_label = tk.Label(self.timestamp_frame, text="00:00")
        self.total_time_label.grid(row=0, column=1, padx=5)

        self.videoTing = tk.Frame(self.root)
        self.videoTing.pack(pady=10)

        # Creating a horizontal frame to group the buttons
        button_frame = tk.Frame(self.videoTing)
        button_frame.pack()

        # Creating the load button
        self.load_button = tk.Button(button_frame, text="Load Video", command=self.load_video)
        self.load_button.pack(padx=10, side=tk.LEFT)

        # Creating multi-video processor button
        self.process_videos_button = tk.Button(button_frame, text="Process Video", command=self.threads_for_videos)
        self.process_videos_button.pack(padx=10, side=tk.LEFT)

        # Clears the loop markers
        self.clear_markers_button = tk.Button(button_frame, text="Clear Markers", command=self.clear_loop_markers)
        self.clear_markers_button.pack(padx=10, side=tk.LEFT)


        # Creating the A-B Loop buttons
        self.loop_buttons_frame = tk.Frame(self.root)
        self.loop_buttons_frame.pack(pady=10)

        self.loop_buttons = {}  # Dictionary to store the loop buttons

    
    def play(self):
        # new try/except block
        # works for when the video freezes
        try:
            self.media_player.play()
        except vlc.VLCException as e:
            # print(f"Error occurred: {e}")
            self.next_frame()
            pass
        # except v

    def pause(self):
        self.media_player.pause()
    
    # new
    def handle_key_press(self, e):
        if e.event_type == keyboard.KEY_DOWN:
            if e.name == 'space':
                self.pause()
            elif e.name == 'left':
                self.rewind()
            elif e.name == 'right':
                self.fast_forward_frames()
    
    # new
    def fast_forward_frames(self):
        self.media_player.set_time(self.media_player.get_time() + 300)  # Fast forward by x a seconds (1000 = 1 second)

    # new
    def release(self):
        # Release VLC resources
        self.media_player.release()
        
        self.root.destroy()  # Close the Tkinter window
        print("Resources DELETED")

    # new + improved
    def undo(self):
        self.read_list_of_tuples(self.time_ranges)

    # new
    def next_frame(self):
        current_time = self.player.get_time()
        new_time = current_time + 150  # Adjust this value as needed
        self.player.set_time(new_time)
        
    def rewind(self):
        rewind_time = 500  # 10 seconds = 10000
        current_time = self.media_player.get_time()
        new_time = max(0, current_time - rewind_time)
        self.media_player.set_time(new_time)


    def update_seek(self, value):
        position = float(value) / 100
        self.media_player.set_position(position)

    def update_timestamps(self):
        if self.media_player.is_playing():
            current_time = self.media_player.get_time() // 1000
            self.current_time_label.config(text=self.format_time(current_time))

            self.seekbar.set(self.media_player.get_position() * 100)

        self.root.after(1000, self.update_timestamps)

    def format_time(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02d}.{minutes:02d}.{seconds:02d}"
    
    def format_time_seconds(self, seconds):
        return f"{seconds:02d}"


    def load_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mkv")])
        if file_path:
            self.video_name = file_path.split("/")[-1]  # Extracting the file name
            media = self.instance.media_new(file_path)
            self.media_player.set_media(media)
            self.media_player.play()

            self.duration = media.get_duration() // 1000
            self.total_time_label.config(text=self.format_time(self.duration))
            self.seekbar.set(0)

            self.update_timestamps()

    def toggle_mute(self):
        if self.muted:
            self.media_player.audio_toggle_mute()  # Toggle mute state
            self.mute_button.config(text="Mute")
            self.muted = False
        else:
            self.media_player.audio_toggle_mute()  # Toggle mute state
            self.mute_button.config(text="Unmute")
            self.muted = True

    def create_loop_button(self, button_names):
        num_cols = 3  # Number of columns in the grid layout
        for i, name in enumerate(button_names):
            if name in self.loop_buttons:
                continue

            loop_button = tk.Button(
                self.loop_buttons_frame,
                text=name,
                command=lambda n=name: self.toggle_loop_marker(n)
            )
            loop_button.grid(row=i // num_cols, column=i % num_cols, padx=5, pady=5)

            self.loop_buttons[name] = loop_button
    
    
    def toggle_loop_marker(self, loop_name):
        if loop_name not in self.loop_markers:
            self.loop_markers[loop_name] = []
            self.loop_buttons[loop_name].config(relief=tk.SUNKEN)
            current_time = self.media_player.get_time() // 1000
            current_time_mil = self.media_player.get_time() / 1000
            self.loop_markers[loop_name].append({"startTime": current_time, "startTimeMil": current_time_mil, "endTime": None, "endTimeMil": None})
        else:
            current_entry = self.loop_markers[loop_name][-1]
            current_time = self.media_player.get_time() // 1000
            current_time_mil = self.media_player.get_time() / 1000
            if current_entry["endTime"] is None:
                current_entry["endTime"] = current_time
                current_entry["endTimeMil"] = current_time_mil
                self.loop_buttons[loop_name].config(relief=tk.RAISED)
                self.time_ranges.append((loop_name, current_entry["startTimeMil"], current_entry["endTimeMil"]))
                self.print_video_markers()
            else:
                self.loop_markers[loop_name].append({"startTime": current_time, "startTimeMil": current_time_mil, "endTime": None, "endTimeMil": None})
                self.loop_buttons[loop_name].config(relief=tk.SUNKEN)

    
    def print_video_markers(self):
        print("Loop Markers:")
        for loop_name, loop_entries in self.loop_markers.items():
            for entry in loop_entries:
                start_time = self.format_time(entry["startTime"])
                end_time = self.format_time(entry["endTime"])
                print(f"{loop_name}: {start_time} - {end_time}")
                
        #print(self.time_ranges)
        #print(self.loop_markers)

    # new
    def read_list_of_tuples(self, my_list):
        if not my_list:  # Check if the list is empty
            return None

        last_tuple = my_list[-1]  # Get the last tuple in the list
        first_item = last_tuple[0]  # Read the first item of the tuple

        if first_item in self.loop_markers:  # Check if the item exists in the dictionary
            if self.loop_markers[first_item]:  # Check if the value list is not empty
                self.loop_markers[first_item].pop()  # Remove the last item from the list

        print("Undo done")
        return self.loop_markers
    
    # new
    def create_cut_video(self, input_filename, start_time, end_time, positions):
        if not os.path.exists(positions):
            os.makedirs(positions)

        # specify here! NB
        try:
            video_folder = r"C:\path\to\your\videos"
        
            video_file = os.path.join(video_folder, input_filename)
            if not os.path.exists(video_file):
                raise FileNotFoundError(f"Error: The video file '{input_filename}' was not found in the folder '{video_folder}'. Please check your file path. [video-cutter.py; line 280-300]")
            
        except Exception as e:
            print("An unexpected error occurred:", e)

        with VideoFileClip(video_file) as input_video:
            start_frame = int(start_time * input_video.fps)
            end_frame = int(end_time * input_video.fps)
            desired_part = input_video.subclip(start_frame / input_video.fps, end_frame / input_video.fps)

            random_number = random.randint(1, 1000)
            output_filename = f"{labels}/{labels}_{start_time:.2f}s_{end_time:.2f}s_{random_number}.mp4"

            desired_part.write_videofile(output_filename, codec="libx264")

    
    def process_video_thread(self, input_filename, start_time, end_time, prodHouse):
        thread = threading.Thread(target=self.create_cut_video, args=(input_filename, start_time, end_time, prodHouse))
        thread.start()
        return thread
    
    def threads_for_videos(self):
        input_filename = self.video_name
        if self.media_player.is_playing():
            self.media_player.pause()

        threads = []

        for prodHouse, start_time, end_time in self.time_ranges:
            thread = self.process_video_thread(input_filename, start_time, end_time, prodHouse)
            threads.append(thread)

        for thread in threads:
            thread.join()

        print("All threads have finished.")
        

    def clear_loop_markers(self):
        self.loop_markers.clear()
        self.time_ranges.clear()
    
    def run(self):
        self.root.mainloop()

# Creating the main window
root = tk.Tk()

# Creating an instance of the VideoCutter
app = VideoCutter(root)


# Add more loop buttons as needed with theor own title.
labels = ['label_1', 'label_2', 'label_3']

# Creating A-B Loop buttons
app.create_loop_button(labels)

# Running the application
app.run()