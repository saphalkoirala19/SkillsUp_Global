import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import pytesseract
import os
import requests  

# Tesseract path execution
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def verify_details_from_api(extracted_text):
    """
    This function simulates verifying extracted text with some API.
    Replace with actual API logic.
    """
    try:
        provided_name = ""

        if provided_name in extracted_text:
            response = requests.get("https://jsonplaceholder.typicode.com/posts/1")
            if response.status_code == 200:
                return "Verified"
            else:
                return "Detail not verified"
        else:
            return "Name not found in certificate"

    except Exception as e:
        return f"API Error: {str(e)}"

def check_certificate(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img).lower()

        certificate_words = ["certificate", "award", "recognize", "complete", "participat"]
        matches = sum(1 for word in certificate_words if word in text)

        if matches >= 2:
            api_result = verify_details_from_api(text)
            return f"Real Certificate\n{api_result}"
        else:
            return "Fake Certificate"
            
    except Exception as e:
        return f"Error: {str(e)}"

def upload_file():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
    if file_path:
        result = check_certificate(file_path)
        messagebox.showinfo("Result", result)

# GUI
window = tk.Tk()
window.title("Certificate Verifier")
window.geometry("400x220")
window.configure(bg="#f4f6f8")

# Style OF GUI
style = ttk.Style()
style.theme_use("clam")
style.configure("TButton",
                font=("Segoe UI", 12, "bold"), foreground="#ffffff",background="#4a90e2", padding=10)
style.map("TButton",
          background=[("active", "#357ABD")])

style.configure("TLabel",
                font=("Segoe UI", 14), foreground="#333333")

# Frame and layout
frame = ttk.Frame(window, padding=20, style="TFrame")
frame.pack(expand=True)

label = ttk.Label(frame, text="Upload Certificate Image", style="TLabel")
label.pack(pady=(10, 15))

button = ttk.Button(frame, text="Browse Image", command=upload_file)
button.pack(ipadx=10)

window.mainloop()
