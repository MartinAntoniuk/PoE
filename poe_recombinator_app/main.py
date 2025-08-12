import tkinter as tk
from tkinter import ttk
from calculator import calculate_recombination_outcomes

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PoE Recombinator Calculator")
        self.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        # Input frame
        input_frame = ttk.LabelFrame(self, text="Desired Outcome")
        input_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(input_frame, text="Desired Prefixes:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.desired_prefixes = tk.IntVar(value=3)
        ttk.Entry(input_frame, textvariable=self.desired_prefixes).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Maximum Suffixes:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.max_suffixes = tk.IntVar(value=2)
        ttk.Entry(input_frame, textvariable=self.max_suffixes).grid(row=1, column=1, padx=5, pady=5)

        # Calculate button
        calculate_button = ttk.Button(self, text="Calculate Best Options", command=self.calculate)
        calculate_button.pack(pady=10)

        # Results frame
        results_frame = ttk.LabelFrame(self, text="Top 5 Crafting Options")
        results_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.results_text = tk.Text(results_frame, height=20, width=90, wrap="word")
        self.results_text.pack(padx=5, pady=5, fill="both", expand=True)

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(self.results_text, command=self.results_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.results_text.config(yscrollcommand=scrollbar.set)


    def calculate(self):
        desired_prefixes = self.desired_prefixes.get()
        max_suffixes = self.max_suffixes.get()

        if not (1 <= desired_prefixes <= 3 and 0 <= max_suffixes <= 3):
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert(tk.END, "Error: Please enter valid numbers for prefixes (1-3) and suffixes (0-3).")
            return

        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(tk.END, "Calculating...")
        self.update_idletasks() # To show the "Calculating..." message

        try:
            options = calculate_recombination_outcomes(desired_prefixes, max_suffixes)
            self.results_text.delete("1.0", tk.END)

            if not options:
                self.results_text.insert(tk.END, "No viable crafting options found for the desired outcome.")
                return

            for i, option in enumerate(options):
                self.results_text.insert(tk.END, f"--- Option {i+1} ---\n")
                self.results_text.insert(tk.END, f"Success Chance: {option['chance']:.2%}\n\n")
                self.results_text.insert(tk.END, f"{option['explanation']}\n\n")

        except Exception as e:
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert(tk.END, f"An error occurred during calculation:\n{e}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
