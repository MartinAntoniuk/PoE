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
        input_frame = ttk.LabelFrame(self, text="Desired Outcome")
        input_frame.pack(padx=10, pady=10, fill="x")

        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)

        ttk.Label(input_frame, text="Desired Prefixes:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.desired_prefixes = tk.IntVar(value=3)
        ttk.Entry(input_frame, textvariable=self.desired_prefixes).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Desired Suffixes:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.desired_suffixes = tk.IntVar(value=0)
        ttk.Entry(input_frame, textvariable=self.desired_suffixes).grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        calculate_button = ttk.Button(self, text="Calculate Best Options", command=self.calculate)
        calculate_button.pack(pady=10)

        results_frame = ttk.LabelFrame(self, text="Top 5 Crafting Plans (sorted by lowest recombination cost)")
        results_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.results_text = tk.Text(results_frame, height=20, width=90, wrap="word")
        self.results_text.pack(padx=5, pady=5, fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.results_text, command=self.results_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.results_text.config(yscrollcommand=scrollbar.set)

    def calculate(self):
        desired_prefixes = self.desired_prefixes.get()
        desired_suffixes = self.desired_suffixes.get()

        if not (0 <= desired_prefixes <= 3 and 0 <= desired_suffixes <= 3):
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert(tk.END, "Error: Please enter valid numbers for affixes (0-3).")
            return

        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(tk.END, "Calculating optimal crafting plans...")
        self.update_idletasks()

        try:
            # This call will be updated in the next step to match the new signature
            plans = calculate_recombination_outcomes(
                desired_prefixes, desired_suffixes
            )
            self.results_text.delete("1.0", tk.END)

            if not plans:
                self.results_text.insert(tk.END, "No viable crafting plans found for the desired outcome.")
                return

            for i, plan in enumerate(plans):
                self.results_text.insert(tk.END, f"--- Plan {i+1}: {plan['name']} ---\n")
                self.results_text.insert(tk.END, f"Total Expected Recombinations: {plan['cost']:.1f}\n")
                self.results_text.insert(tk.END, f"Total Exclusive Mods Needed: {plan['exclusive_cost']}\n\n")
                self.results_text.insert(tk.END, f"**Full Plan:**\n{plan['explanation']}\n\n")

        except Exception as e:
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert(tk.END, f"An error occurred during calculation:\n{e}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
