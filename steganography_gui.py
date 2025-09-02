import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
from steganography_tool import SteganographyTool
import cv2
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class SteganographyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Steganography Tool - IKB21303 Assignment 2")
        self.root.geometry("900x900")

        self.stego_tool = SteganographyTool()
        self.cover_image_path = tk.StringVar()
        self.secret_file_path = tk.StringVar()
        self.stego_image_path = tk.StringVar()
        self.extract_stego_path = tk.StringVar()
        self.extract_output_path = tk.StringVar()
        self.analysis_original_path = tk.StringVar()
        self.analysis_stego_path = tk.StringVar()
        self.histogram_save_path = tk.StringVar(value="histogram_comparison.png")

        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(self.root, text="🔒 Steganography Tool",
                               font=("Arial", 20, "bold"), fg="navy")
        title_label.pack(pady=10)

        subtitle_label = tk.Label(self.root, text="Hide and Extract Files in Images",
                                  font=("Arial", 12), fg="gray")
        subtitle_label.pack(pady=(0, 20))

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=20, pady=10)

        hide_frame = ttk.Frame(notebook)
        notebook.add(hide_frame, text="🔒 Hide Data")
        self.create_hide_tab(hide_frame)

        extract_frame = ttk.Frame(notebook)
        notebook.add(extract_frame, text="🔓 Extract Data")
        self.create_extract_tab(extract_frame)

        analysis_frame = ttk.Frame(notebook)
        notebook.add(analysis_frame, text="📊 Analysis")
        self.create_analysis_tab(analysis_frame)

        exit_button = ttk.Button(self.root, text="Exit", command=self.root.destroy)
        exit_button.pack(pady=10)

    def create_hide_tab(self, parent):
        cover_group = ttk.LabelFrame(parent, text="Step 1: Select Cover Image")
        cover_group.pack(fill="x", padx=10, pady=10)
        ttk.Label(cover_group, text="Choose an image to hide data in:").pack(anchor="w", padx=5, pady=5)
        cover_frame = ttk.Frame(cover_group)
        cover_frame.pack(fill="x", padx=5, pady=5)
        ttk.Entry(cover_frame, textvariable=self.cover_image_path, width=60).pack(side="left", padx=(0, 5))
        ttk.Button(cover_frame, text="Browse", command=self.select_cover_image).pack(side="right")

        secret_group = ttk.LabelFrame(parent, text="Step 2: Select Secret File")
        secret_group.pack(fill="x", padx=10, pady=10)
        ttk.Label(secret_group, text="Choose file to hide (text, PDF, image, etc.):").pack(anchor="w", padx=5, pady=5)
        secret_frame = ttk.Frame(secret_group)
        secret_frame.pack(fill="x", padx=5, pady=5)
        ttk.Entry(secret_frame, textvariable=self.secret_file_path, width=60).pack(side="left", padx=(0, 5))
        ttk.Button(secret_frame, text="Browse", command=self.select_secret_file).pack(side="right")

        output_group = ttk.LabelFrame(parent, text="Step 3: Output Settings")
        output_group.pack(fill="x", padx=10, pady=10)
        ttk.Label(output_group, text="Stego image will be saved as:").pack(anchor="w", padx=5, pady=5)
        output_frame = ttk.Frame(output_group)
        output_frame.pack(fill="x", padx=5, pady=5)
        ttk.Entry(output_frame, textvariable=self.stego_image_path, width=60).pack(side="left", padx=(0, 5))
        ttk.Button(output_frame, text="Browse", command=self.select_stego_output).pack(side="right")

        hide_button = ttk.Button(parent, text="🔒 Hide Data in Image",
                                 command=self.hide_data, style="Accent.TButton")
        hide_button.pack(pady=20)
        self.hide_progress = ttk.Progressbar(parent, mode='indeterminate')
        self.hide_progress.pack(fill="x", padx=10, pady=5)
        self.hide_status = tk.Text(parent, height=8, wrap=tk.WORD)
        self.hide_status.pack(fill="both", expand=True, padx=10, pady=10)

    def create_extract_tab(self, parent):
        stego_group = ttk.LabelFrame(parent, text="Step 1: Select Stego Image")
        stego_group.pack(fill="x", padx=10, pady=10)
        ttk.Label(stego_group, text="Choose the stego image containing hidden data:").pack(anchor="w", padx=5, pady=5)
        stego_frame = ttk.Frame(stego_group)
        stego_frame.pack(fill="x", padx=5, pady=5)
        ttk.Entry(stego_frame, textvariable=self.extract_stego_path, width=60).pack(side="left", padx=(0, 5))
        ttk.Button(stego_frame, text="Browse", command=self.select_extract_stego).pack(side="right")

        extract_output_group = ttk.LabelFrame(parent, text="Step 2: Output Settings")
        extract_output_group.pack(fill="x", padx=10, pady=10)
        ttk.Label(extract_output_group, text="Extracted file will be saved as:").pack(anchor="w", padx=5, pady=5)
        extract_frame = ttk.Frame(extract_output_group)
        extract_frame.pack(fill="x", padx=5, pady=5)
        ttk.Entry(extract_frame, textvariable=self.extract_output_path, width=60).pack(side="left", padx=(0, 5))
        ttk.Button(extract_frame, text="Browse", command=self.select_extract_output).pack(side="right")

        extract_button = ttk.Button(parent, text="🔓 Extract Hidden Data",
                                    command=self.extract_data, style="Accent.TButton")
        extract_button.pack(pady=20)
        self.extract_progress = ttk.Progressbar(parent, mode='indeterminate')
        self.extract_progress.pack(fill="x", padx=10, pady=5)
        self.extract_status = tk.Text(parent, height=8, wrap=tk.WORD)
        self.extract_status.pack(fill="both", expand=True, padx=10, pady=10)

    def create_analysis_tab(self, parent):
        # Create a scrollable container
        main_canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)

        # Analysis controls
        analysis_group = ttk.LabelFrame(scrollable_frame, text="Image Analysis")
        analysis_group.pack(fill="x", padx=10, pady=10)
        ttk.Label(analysis_group, text="Compare original and stego images:").pack(anchor="w", padx=5, pady=5)
        
        orig_frame = ttk.Frame(analysis_group)
        orig_frame.pack(fill="x", padx=5, pady=5)
        ttk.Label(orig_frame, text="Original:").pack(side="left", padx=(0, 5))
        ttk.Entry(orig_frame, textvariable=self.analysis_original_path, width=50).pack(side="left", padx=(0, 5))
        ttk.Button(orig_frame, text="Browse", command=self.select_analysis_original).pack(side="right")

        stego_analysis_frame = ttk.Frame(analysis_group)
        stego_analysis_frame.pack(fill="x", padx=5, pady=5)
        ttk.Label(stego_analysis_frame, text="Stego:").pack(side="left", padx=(0, 5))
        ttk.Entry(stego_analysis_frame, textvariable=self.analysis_stego_path, width=50).pack(side="left", padx=(0, 5))
        ttk.Button(stego_analysis_frame, text="Browse", command=self.select_analysis_stego).pack(side="right")

        save_hist_frame = ttk.Frame(analysis_group)
        save_hist_frame.pack(fill="x", padx=5, pady=5)
        ttk.Label(save_hist_frame, text="Save Histogram As:").pack(side="left", padx=(0, 5))
        ttk.Entry(save_hist_frame, textvariable=self.histogram_save_path, width=40).pack(side="left", padx=(0, 5))
        ttk.Button(save_hist_frame, text="Browse Save Location", command=self.select_histogram_save_path).pack(side="right")

        analyze_button = ttk.Button(scrollable_frame, text="📊 Analyze Images",
                                   command=self.analyze_images, style="Accent.TButton")
        analyze_button.pack(pady=10)

        # Graph frame for histograms
        self.graph_frame = ttk.Frame(scrollable_frame)
        self.graph_frame.pack(fill="x", padx=10, pady=10)

        # Table for metrics - will be visible below graphs
        self.analysis_table = ttk.Treeview(scrollable_frame, columns=('Metric', 'Original', 'Stego', 'Comparison'), 
                                         show='headings', height=7)
        self.analysis_table.heading('Metric', text='Metric')
        self.analysis_table.heading('Original', text='Original')
        self.analysis_table.heading('Stego', text='Stego')
        self.analysis_table.heading('Comparison', text='Comparison')
        self.analysis_table.column('Metric', width=180, anchor='w')
        self.analysis_table.column('Original', width=110, anchor='center')
        self.analysis_table.column('Stego', width=110, anchor='center')
        self.analysis_table.column('Comparison', width=180, anchor='center')
        self.analysis_table.pack(fill="x", padx=10, pady=10)

        # Pack the canvas and scrollbar
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def select_cover_image(self):
        filename = filedialog.askopenfilename(
            title="Select Cover Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")]
        )
        if filename:
            self.cover_image_path.set(filename)
            base_name = os.path.splitext(filename)[0]
            self.stego_image_path.set(f"{base_name}_stego.png")

    def select_secret_file(self):
        filename = filedialog.askopenfilename(
            title="Select Secret File",
            filetypes=[("All files", "*.*"), ("Text files", "*.txt"), ("PDF files", "*.pdf")]
        )
        if filename:
            self.secret_file_path.set(filename)

    def select_stego_output(self):
        filename = filedialog.asksaveasfilename(
            title="Save Stego Image As",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if filename:
            self.stego_image_path.set(filename)

    def select_extract_stego(self):
        filename = filedialog.askopenfilename(
            title="Select Stego Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")]
        )
        if filename:
            self.extract_stego_path.set(filename)
            base_name = os.path.splitext(os.path.basename(filename))[0]
            self.extract_output_path.set(f"extracted_{base_name}")

    def select_extract_output(self):
        filename = filedialog.asksaveasfilename(
            title="Save Extracted File As",
            filetypes=[("All files", "*.*")]
        )
        if filename:
            self.extract_output_path.set(filename)

    def select_analysis_original(self):
        filename = filedialog.askopenfilename(
            title="Select Original Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")]
        )
        if filename:
            self.analysis_original_path.set(filename)

    def select_analysis_stego(self):
        filename = filedialog.askopenfilename(
            title="Select Stego Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")]
        )
        if filename:
            self.analysis_stego_path.set(filename)

    def select_histogram_save_path(self):
        filename = filedialog.asksaveasfilename(
            title="Save Histogram As",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if filename:
            self.histogram_save_path.set(filename)

    def hide_data(self):
        if not all([self.cover_image_path.get(), self.secret_file_path.get(), self.stego_image_path.get()]):
            messagebox.showerror("Error", "Please select all required files!")
            return

        def hide_thread():
            try:
                self.hide_progress.start()
                self.hide_status.delete(1.0, tk.END)
                self.hide_status.insert(tk.END, "Starting hiding process...\n")

                cover_size = os.path.getsize(self.cover_image_path.get())
                secret_size = os.path.getsize(self.secret_file_path.get())

                self.hide_status.insert(tk.END, f"Cover image size: {cover_size:,} bytes\n")
                self.hide_status.insert(tk.END, f"Secret file size: {secret_size:,} bytes\n")

                self.stego_tool.hide_data_in_image(
                    self.cover_image_path.get(),
                    self.secret_file_path.get(),
                    self.stego_image_path.get()
                )

                stego_size = os.path.getsize(self.stego_image_path.get())
                self.hide_status.insert(tk.END, f"Stego image size: {stego_size:,} bytes\n")
                self.hide_status.insert(tk.END, f"Size change: {stego_size - cover_size:+,} bytes\n")
                self.hide_status.insert(tk.END, "\n✅ Data hidden successfully!\n")

                self.hide_progress.stop()
                messagebox.showinfo("Success", "Data hidden successfully in the image!")

            except Exception as e:
                self.hide_progress.stop()
                self.hide_status.insert(tk.END, f"\n❌ Error: {str(e)}\n")
                messagebox.showerror("Error", f"Failed to hide data: {str(e)}")

        threading.Thread(target=hide_thread, daemon=True).start()

    def extract_data(self):
        if not all([self.extract_stego_path.get(), self.extract_output_path.get()]):
            messagebox.showerror("Error", "Please select all required files!")
            return

        def extract_thread():
            try:
                self.extract_progress.start()
                self.extract_status.delete(1.0, tk.END)
                self.extract_status.insert(tk.END, "Starting extraction process...\n")

                extracted_file = self.stego_tool.extract_data_from_image(
                    self.extract_stego_path.get(),
                    self.extract_output_path.get()
                )

                extracted_size = os.path.getsize(extracted_file)
                self.extract_status.insert(tk.END, f"Extracted file: {extracted_file}\n")
                self.extract_status.insert(tk.END, f"Extracted file size: {extracted_size:,} bytes\n")
                self.extract_status.insert(tk.END, "\n✅ Data extracted successfully!\n")

                self.extract_progress.stop()
                messagebox.showinfo("Success", f"Data extracted successfully to: {extracted_file}")

            except Exception as e:
                self.extract_progress.stop()
                self.extract_status.insert(tk.END, f"\n❌ Error: {str(e)}\n")
                messagebox.showerror("Error", f"Failed to extract data: {str(e)}")

        threading.Thread(target=extract_thread, daemon=True).start()

    def analyze_images(self):
        if not all([self.analysis_original_path.get(), self.analysis_stego_path.get()]):
            messagebox.showerror("Error", "Please select both images to analyze!")
            return

        def analyze_thread():
            try:
                for widget in self.graph_frame.winfo_children():
                    widget.destroy()

                analysis = self.stego_tool.analyze_images(
                    self.analysis_original_path.get(),
                    self.analysis_stego_path.get()
                )

                original = cv2.imread(self.analysis_original_path.get())
                stego = cv2.imread(self.analysis_stego_path.get())

                if len(original.shape) == 2:
                    original = cv2.cvtColor(original, cv2.COLOR_GRAY2BGR)
                if len(stego.shape) == 2:
                    stego = cv2.cvtColor(stego, cv2.COLOR_GRAY2BGR)
                if original.shape[2] > 3:
                    original = original[:, :, :3]
                if stego.shape[2] > 3:
                    stego = stego[:, :, :3]

                original_rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
                stego_rgb = cv2.cvtColor(stego, cv2.COLOR_BGR2RGB)

                fig, axes = plt.subplots(2, 4, figsize=(16, 8))
                axes[0, 0].imshow(original_rgb)
                axes[0, 0].set_title('Original Image')
                axes[0, 0].axis('off')
                axes[1, 0].imshow(stego_rgb)
                axes[1, 0].set_title('Stego Image')
                axes[1, 0].axis('off')

                colors = ['red', 'green', 'blue']
                for i, color in enumerate(colors):
                    hist_orig = cv2.calcHist([original], [i], None, [256], [0, 256])
                    axes[0, i + 1].plot(hist_orig, color=color)
                    axes[0, i + 1].set_title(f'Original - {color.capitalize()} Channel')
                    axes[0, i + 1].set_xlim([0, 256])

                    hist_stego = cv2.calcHist([stego], [i], None, [256], [0, 256])
                    axes[1, i + 1].plot(hist_stego, color=color)
                    axes[1, i + 1].set_title(f'Stego - {color.capitalize()} Channel')
                    axes[1, i + 1].set_xlim([0, 256])

                axes[0, 3].axis('off')
                axes[1, 3].axis('off')

                plt.tight_layout()
                histogram_path = self.histogram_save_path.get()
                plt.savefig(histogram_path, dpi=300, bbox_inches='tight')

                canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True)
                plt.close(fig)

                psnr = analysis['psnr']
                mse = analysis['mse']
                original_size = analysis['original_size']
                stego_size = analysis['stego_size']
                size_diff = stego_size - original_size
                size_change_pct = (size_diff / original_size) * 100
                if psnr > 30:
                    quality = "Excellent (visually identical)"
                elif psnr > 20:
                    quality = "Good (minimal visible difference)"
                else:
                    quality = "Poor (visible differences)"

                for item in self.analysis_table.get_children():
                    self.analysis_table.delete(item)

                comparison_rows = [
                    ("Image Size (bytes)", f"{original_size:,}", f"{stego_size:,}", f"{size_diff:+,}"),
                    ("Size Change (%)", "", "", f"{size_change_pct:+.2f}%"),
                    ("MSE (Mean Squared Error)", f"{mse:.4f}", "", ""),
                    ("PSNR (dB)", f"{psnr:.2f}", "", ""),
                    ("Quality", "", "", quality),
                    ("Histogram Saved", "", "", histogram_path),
                ]
                for row in comparison_rows:
                    self.analysis_table.insert("", "end", values=row)

                messagebox.showinfo("Analysis Complete", "Image analysis completed successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to analyze images: {str(e)}")

        threading.Thread(target=analyze_thread, daemon=True).start()

def main():
    root = tk.Tk()
    app = SteganographyGUI(root)
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    root.mainloop()

if __name__ == "__main__":
    main()
