import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import threading
import requests
import urllib3
import os
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class VideoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Eye of Veritas")
        self.root.geometry("800x600")
        self.root.config(bg="#1E1B4B")

        self.video_filename = "recorded_video.mp4"
        self.recording = False
        self.cap = None
        self.form_visible = False
        self.setup_ui()

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS  
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def authenticate_user(self, email, password):
        url = "https://apipermisson.runasp.net/api/Auth/login"
        payload = {"Email": email, "Password": password}
        try:
            response = requests.post(url, json=payload, verify=False)
            if response.status_code == 200:
                data = response.json()
                return data.get("isAuthenticated", False), data.get("token", ""), data.get("userName", "")
            return False, "", ""
        except Exception as e:
            print("API Error:", e)
            return False, "", ""

    def record_video(self):
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(self.video_filename, fourcc, 20.0, (300, 150))  # Reduced height to 150
        while self.recording and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                resized_frame = cv2.resize(frame, (300, 150))  # Reduced height to 150
                out.write(resized_frame)
                self.show_frame(resized_frame)
            else:
                break
        out.release()
        if self.cap:
            self.cap.release()
        self.form_visible = True
        self.root.after(0, self.show_form)
        self.root.after(0, lambda: self.show_video_preview(self.video_filename))

    def show_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_preview.imgtk = imgtk
        self.video_preview.configure(image=imgtk, text="")

    def update_camera(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                resized_frame = cv2.resize(frame, (300, 150))  # Reduced height to 150
                self.show_frame(resized_frame)
            if self.recording:
                self.root.after(10, self.update_camera)

    def start_recording(self):
        self.recording = True
        self.cap = cv2.VideoCapture(0)
        self.update_camera()
        threading.Thread(target=self.record_video, daemon=True).start()
        self.btn_record.config(text="Stop Recording", command=self.stop_recording)

    def stop_recording(self):
        self.recording = False
        self.btn_record.config(text="Start Recording", command=self.start_recording)
        messagebox.showinfo("Recording Saved", f"Video saved as {self.video_filename}")
        self.form_visible = True
        self.root.after(0, self.show_form)
        self.root.after(0, lambda: self.show_video_preview(self.video_filename))

    def browse_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mov")])
        if file_path:
            self.video_filename = file_path
            messagebox.showinfo("Selected", f"Selected file: {file_path}")
            self.form_visible = True
            self.root.after(0, self.show_form)
            self.root.after(0, lambda: self.show_video_preview(self.video_filename))

    def show_video_preview(self, path):
        cap_preview = cv2.VideoCapture(path)
        ret, frame = cap_preview.read()
        if ret:
            resized_frame = cv2.resize(frame, (300, 150))  # Reduced height to 150
            self.show_frame(resized_frame)
        else:
            self.video_preview.configure(image="", text="Unable to preview video.")
        cap_preview.release()

    def call_prediction_api(self):
        try:
            with open(self.video_filename, "rb") as video:
                files = {"video": ("video.mp4", video, "video/mp4")}
                response = requests.post("https://deception-api-production-cfcd.up.railway.app/predict", files=files)
                if response.status_code == 200:
                    try:
                        result = response.json()
<<<<<<< HEAD
                        self.prediction_text.set(f"Result: {result}")
=======
                        outcome = result.get("result", "Unknown").capitalize()
                        if outcome == "Truth" or outcome == "Lie":
                            self.prediction_text.set( f"Result : {outcome}")
                        else:
                            self.prediction_text.set("Unknown")
>>>>>>> f3772b1 (Update :result ,icon)
                    except Exception:
                        self.prediction_text.set(f"Result: {response.text}")
                else:
                    self.prediction_text.set(f"API Error: {response.status_code}")
        except Exception as e:
            self.prediction_text.set(f"Exception: {str(e)}")
        self.prediction_label.pack(pady=10)
        self.btn_clear.pack(pady=10)

    def upload_video(self):
        name = self.entry_name.get()
        phone = self.entry_id.get()
        if not name or not phone:
            messagebox.showwarning("Missing Info", "Please fill all form fields.")
            return
        if not self.video_filename:
            messagebox.showwarning("Missing Video", "Please select or record a video.")
            return
        self.call_prediction_api()
        self.form_frame.pack_forget()  # Remove the form after submission

    def clear_form(self):
        self.entry_name.delete(0, tk.END)
        self.entry_id.delete(0, tk.END)
        self.prediction_text.set("")
        self.video_preview.configure(image="", text="No video selected.")
        self.video_filename = ""
        self.prediction_label.pack_forget()
        self.btn_clear.pack_forget()
        self.form_frame.pack_forget()
        self.btn_submit.pack_forget()
        self.form_visible = False

    def show_form(self):
        if not self.form_visible:
            return
        self.form_frame.pack(pady=20)
        # Removed self.btn_submit.pack(pady=(0, 10)) to avoid mixing geometry managers

    def setup_ui(self):
        frame = tk.Frame(self.root, bg="#1E1B4B")
        frame.place(relx=0.5, rely=0.35, anchor="center")

        # Title
        tk.Label(frame, text="Eye of Veritas", font=("Georgia", 28, "bold"), fg="white", bg="#1E1B4B").grid(row=0, column=0, pady=(10, 30))

        # Email field
        tk.Label(frame, text="Email", font=("Arial", 14), fg="white", bg="#1E1B4B").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.entry_email = tk.Entry(frame, font=("Arial", 13), fg="white", bg="#1E1B4B", insertbackground="white", bd=0, highlightthickness=1, highlightbackground="white", highlightcolor="white", relief="flat")
        self.entry_email.grid(row=2, column=0, padx=10, pady=(0, 15), sticky="ew")

        # Password field
        tk.Label(frame, text="Password", font=("Arial", 14), fg="white", bg="#1E1B4B").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.entry_password = tk.Entry(frame, font=("Arial", 13), fg="white", bg="#1E1B4B", insertbackground="white", show="*", bd=0, highlightthickness=1, highlightbackground="white", highlightcolor="white", relief="flat")
        self.entry_password.grid(row=4, column=0, padx=10, pady=(0, 25), sticky="ew")

        # Login button
        self.login_button = tk.Label(frame, text="Login", font=("Arial", 14, "bold"), bg="#7D31D6", fg="white", padx=30, pady=12, cursor="hand2")
        self.login_button.grid(row=5, column=0, pady=10)
<<<<<<< HEAD
        self.login_button.bind("<Enter>", lambda e: self.login_button.config(bg="#1E293B"))
        self.login_button.bind("<Leave>", lambda e: self.login_button.config(bg="#7D31D6"))
        self.login_button.bind("<Button-1>", lambda e: self.login_button.config(bg="#0C1A2B"))
=======
        self.login_button.bind("<Enter>", lambda e: self.login_button.config(bg="#2359AF"))
        self.login_button.bind("<Leave>", lambda e: self.login_button.config(bg="#7D31D6"))
        self.login_button.bind("<Button-1>", lambda e: self.login_button.config(bg="#114583"))
>>>>>>> f3772b1 (Update :result ,icon)
        self.login_button.bind("<ButtonRelease-1>", lambda e: self.login_function())

        # Load and display logo
        logo_path = self.resource_path("logo.png")
        print("Logo path:", logo_path)
        if os.path.exists(logo_path):
            logo_image = Image.open(logo_path).resize((90, 90), Image.Resampling.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(self.root, image=logo_photo, bg="#1E1B4B")
            logo_label.image = logo_photo
            logo_label.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)
        else:
            print("Warning: logo.png not found. Skipping logo display.")

    def login_function(self):
        email = self.entry_email.get()
        password = self.entry_password.get()
        success, token, username = self.authenticate_user(email, password)
        if success:
            self.open_service_window(username)
        else:
            self.login_button.config(text="Invalid!", bg="#991B1B")

    def open_service_window(self, username):
        self.root.destroy()
        service_window = tk.Tk()
        service_window.title("Service")
        service_window.geometry("980x550")
        service_window.configure(bg="white")

        tk.Label(service_window, text=f"Welcome, {username}", font=("Georgia", 16, "bold"), fg="#1E1B4B", bg="white").pack(pady=5)
<<<<<<< HEAD
        tk.Label(service_window, text="Service", font=("Georgia", 20, "bold"), fg="#1E1B4B", bg="white").pack()
=======
        
>>>>>>> f3772b1 (Update :result ,icon)

        self.video_preview = tk.Label(service_window, bg="white", text="No video selected.", font=("Arial", 12), fg="gray")
        self.video_preview.pack(pady=10)

        upload_icon_path = self.resource_path("./upload2.png")
        rec_icon_path = self.resource_path("./rec.png")
        print("Upload icon path:", upload_icon_path)
        print("Record icon path:", rec_icon_path)

        if not (os.path.exists(upload_icon_path) and os.path.exists(rec_icon_path)):
            messagebox.showwarning("Resource Error", "Missing icon files (upload2.png or rec.png).")
            return

        upload_icon = ImageTk.PhotoImage(Image.open(upload_icon_path).resize((60, 60)))
        record_icon = ImageTk.PhotoImage(Image.open(rec_icon_path).resize((60, 60)))

        button_frame = tk.Frame(service_window, bg="white")
        button_frame.pack(pady=10)

        upload_frame = tk.Frame(button_frame, bg="white")
        upload_frame.grid(row=0, column=0, padx=30)
        tk.Label(upload_frame, image=upload_icon, bg="white").pack()
        tk.Button(upload_frame, text="Upload Video", bg="#1178B4", fg="white", font=("Arial", 12), width=15, height=1, command=self.browse_video).pack(pady=(10, 0))

        record_frame = tk.Frame(button_frame, bg="white")
        record_frame.grid(row=0, column=1, padx=30)
        tk.Label(record_frame, image=record_icon, bg="white").pack()
        self.btn_record = tk.Button(record_frame, text="Start Recording", bg="#7D31D6", fg="white", font=("Arial", 12), width=15, height=1, command=self.start_recording)
        self.btn_record.pack(pady=(10, 0))

        self.form_frame = tk.Frame(service_window, bg="white", relief="groove")
        tk.Label(self.form_frame, text="Name", fg="#1E1B4B", bg="#F5F7FF", font=("Arial", 14)).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.entry_name = tk.Entry(self.form_frame, font=("Arial", 12), width=25)
        self.entry_name.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.form_frame, text="ID", fg="#1E1B4B", bg="#F5F7FF", font=("Arial", 14)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.entry_id = tk.Entry(self.form_frame, font=("Arial", 12), width=25)
        self.entry_id.grid(row=1, column=1, padx=10, pady=5)

        # Add Submit button below the form fields
        self.btn_submit = tk.Button(self.form_frame, text="Submit", bg="#2D3A98", fg="white", font=("Arial", 14), command=self.upload_video, padx=20, pady=5)
        self.btn_submit.grid(row=2, column=0, columnspan=2, pady=10)  # Place below ID field

        self.form_frame.pack(pady=20)  # Pack the form frame

        self.prediction_text = tk.StringVar()
<<<<<<< HEAD
        self.prediction_label = tk.Label(service_window, textvariable=self.prediction_text, font=("Arial", 12), fg="#1E1B4B", bg="white")
        self.btn_clear = tk.Button(service_window, text="Clear", bg="#991B1B", fg="white", font=("Arial", 12), command=self.clear_form, padx=20, pady=5)

        self.form_visible = True
=======
  
        
        self.prediction_label = tk.Label(service_window, textvariable=self.prediction_text, font=("Arial", 17,"bold"), fg="#1E1B4B", bg="white" )
        self.btn_clear = tk.Button(service_window, text="Clear", bg="#991B1B", fg="white", font=("Arial", 12), command=self.clear_form, padx=20, pady=5)

        self.form_visible = True    
>>>>>>> f3772b1 (Update :result ,icon)
        # No need to call show_form() here since form_frame is packed directly

        logo_path = self.resource_path("logo.png")
        print("Logo path:", logo_path)
        if os.path.exists(logo_path):
            logo_image = Image.open(logo_path).resize((90, 90), Image.Resampling.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(service_window, image=logo_photo, bg="white")
            logo_label.image = logo_photo
            logo_label.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)
        else:
            print("Warning: logo.png not found. Skipping logo display.")

        service_window.mainloop()

if __name__ == "__main__":
    app = VideoApp(tk.Tk())
    app.root.mainloop()