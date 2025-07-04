import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import pytesseract
import pdfplumber
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

#path to Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text(file_path):
    text = ""
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == ".pdf":
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
        elif ext in [".png", ".jpg", ".jpeg"]:
            image = Image.open(file_path)
            text += pytesseract.image_to_string(image)
        elif ext == ".txt":
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
    except Exception as e:
        print(f" Error reading {file_path}: {e}")
    return text.strip()

def analyze_resumes(file_paths):
    resume_texts = [extract_text(path) for path in file_paths]

    # Filter out empty texts
    valid_pairs = [(fp, txt) for fp, txt in zip(file_paths, resume_texts) if txt.strip()]
    if not valid_pairs:
        return " No readable resumes found. Make sure they are clear and text-based."

    filenames, texts = zip(*valid_pairs)

    # Only one file? Return a message
    if len(filenames) == 1:
        return (f"Only one resume uploaded:\n\n"
                f" {os.path.basename(filenames[0])}\n"
                f" Text length: {len(texts[0].split())} words\n"
                f" Tip: Upload multiple resumes for ranking.")

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(texts)

    # Compute pairwise similarity matrix
    similarity_matrix = cosine_similarity(tfidf_matrix)

    if len(filenames) == 2:
        sim = similarity_matrix[0, 1]
        return (f" Resume Ranking (2 resumes only):\n"
                f"\n1. {os.path.basename(filenames[0])}"
                f"\n2. {os.path.basename(filenames[1])}"
                f"\n\nSimilarity Score: {sim:.2f} (0 = different, 1 = identical)")

    # Average similarity (excluding self)
    avg_similarities = []
    for i in range(len(filenames)):
        sim_sum = np.sum(similarity_matrix[i]) - 1
        avg_sim = sim_sum / (len(filenames) - 1)
        avg_similarities.append(avg_sim)

    # Normalize to 0-100
    max_sim = np.max(avg_similarities)
    min_sim = np.min(avg_similarities)
    range_sim = max_sim - min_sim if max_sim != min_sim else 1
    scores = [(sim - min_sim) / range_sim * 100 for sim in avg_similarities]

    # Sort
    ranking = sorted(zip(filenames, scores, avg_similarities), key=lambda x: x[1], reverse=True)

    result_text = "Resume Ranking Results:"
    for i, (filename, score, sim) in enumerate(ranking, 1):
        result_text += f"\n{i}. {os.path.basename(filename)}\n    Score: {int(score)}/100\n   Similarity Avg: {sim:.2f}\n"
    return result_text

class ResumeRankerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Resume Ranker (PDF, Image, TXT)")
        self.root.geometry("880x600")
        self.files = []

        ttk.Label(root, text=" Resume Ranker Tool", font=("Arial", 20, "bold")).pack(pady=10)

        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text=" Upload Resumes", command=self.upload_files).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text=" Analyze & Rank", command=self.analyze).grid(row=0, column=1, padx=10)

        self.text_area = tk.Text(root, wrap="word", font=("Consolas", 11))
        self.text_area.pack(padx=15, pady=15, fill="both", expand=True)
        self.text_area.config(state="disabled")

    def upload_files(self):
        filetypes = [("Supported Files", "*.pdf *.png *.jpg *.jpeg *.txt")]
        self.files = filedialog.askopenfilenames(filetypes=filetypes)
        if self.files:
            messagebox.showinfo(" Upload Successful", f"{len(self.files)} resume(s) selected.")

    def analyze(self):
        if not self.files:
            messagebox.showwarning(" No Files", "Please upload at least one resume.")
            return
        result = analyze_resumes(self.files)
        self.text_area.config(state="normal")
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, result)
        self.text_area.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = ResumeRankerApp(root)
    root.mainloop()
