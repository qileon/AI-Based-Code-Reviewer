import customtkinter as ctk # this is a modern version of tkinter for ui
from tkinter import messagebox # used to show small popup messages
from google import genai # used to connect with google ai
import time # used for waiting
import pyperclip # used to copy text to clipboard
import sys # used to stop the program if file is missing
import os # used to find the exact file path reliably

# color settings for the app
ctk.set_appearance_mode("dark") # dark mode
ctk.set_default_color_theme("blue") # blue theme

# find the exact folder where this python file is located
script_dir = os.path.dirname(os.path.abspath(__file__))
api_file_path = os.path.join(script_dir, "api_key.txt")

# gemini api key connection
# read the api key from the text file securely
try:
    with open(api_file_path, "r", encoding="utf-8") as file:
        API_KEY = file.read().strip() # remove any extra spaces or newlines
        
    # check if the file is accidentally empty
    if not API_KEY:
        raise ValueError("File is empty")
        
except (FileNotFoundError, ValueError):
    # create a temporary hidden window so the error message shows up properly without freezing
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    
    # show an error if the user forgot to create the file or left it empty
    messagebox.showerror("Error", f"API Key not found or empty!\n\nPlease make sure your key is inside this file:\n{api_file_path}")
    sys.exit() # close the program safely

client = genai.Client(api_key=API_KEY)

# this is the main class that creates and controls the whole app window
class ModernCodeReviewer(ctk.CTk):
    def __init__(self):
        # __init__ runs automatically when the app starts
        super().__init__()

        # window settings
        # these lines set the title, size, and background color of the window
        self.title("AI Based Code Reviewer")
        self.geometry("1080x860")
        self.configure(fg_color="#343a40")

        # layout will adjust when window resizes
        # column 1 (right side) will grow when the window gets bigger
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # sidebar on the left
        # this creates the dark panel on the left side of the window
        self.sidebar = ctk.CTkFrame(self, width=185, corner_radius=0, fg_color="#212529")
        # no need for width since we used "True"
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(True)

        # sidebar title
        # this shows the word "CONTROLS" at the top of the left panel
        self.side_label = ctk.CTkLabel(self.sidebar, text="CONTROLS", font=("Arial", 20, "bold"), text_color="#3b82f6")
        self.side_label.grid(row=0, column=0, padx=20, pady=(30, 20))

        # label for selecting code language
        # this is a small text that says which dropdown is below it
        self.lang_label = ctk.CTkLabel(self.sidebar, text="Code Language:", font=("Arial", 12))
        self.lang_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")

        # dropdown menu for languages
        # the user clicks here to choose what coding language their code is written in
        self.lang_menu = ctk.CTkOptionMenu(self.sidebar, values=["Python", "JavaScript", "C++", "Java", "C#"])
        self.lang_menu.set("Python")
        self.lang_menu.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        # button to copy report
        # when clicked, this copies the ai result text so the user can paste it somewhere else
        self.copy_btn = ctk.CTkButton(self.sidebar, text="COPY REPORT 📋", fg_color="#28a745", hover_color="#218838", font=("Arial", 13, "bold"), command=self.copy_report)
        self.copy_btn.grid(row=3, column=0, padx=20, pady=20, sticky="ew")

        # button to clear all text
        # this deletes everything in both the input and output boxes
        self.clear_btn = ctk.CTkButton(self.sidebar, text="CLEAR ALL 🗑️", fg_color="#dc3545", hover_color="#c82333", font=("Arial", 13, "bold"), command=self.clear_all)
        self.clear_btn.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        # small info text
        # this reminds the user they can press shift+enter instead of clicking the button
        self.info_label = ctk.CTkLabel(self.sidebar, text="Shift + Enter to Run", font=("Arial", 11), text_color="gray")
        self.info_label.grid(row=10, column=0, padx=20, pady=20, sticky="s")
        self.sidebar.grid_rowconfigure(10, weight=1)

        # main area on the right
        # this is the bigger bottom area where the user types code and sees the ai result
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(1, weight=1)
        self.main_area.grid_rowconfigure(4, weight=2)

        # label for code input
        # this is the title text above the box where the user types their code
        self.in_lbl = ctk.CTkLabel(self.main_area, text="SOURCE CODE", font=("Arial", 13, "bold"))
        self.in_lbl.grid(row=0, column=0, sticky="w", pady=(0, 5))

        # textbox where user writes code
        # this is the big box at the top where the user pastes or types their code
        self.input_box = ctk.CTkTextbox(self.main_area, font=("Consolas", 14), fg_color="#495057", border_width=1)
        self.input_box.grid(row=1, column=0, sticky="nsew", pady=5)

        # button to start ai analysis
        # clicking this sends the code to google ai and waits for the review result
        self.analyze_btn = ctk.CTkButton(self.main_area, text="RUN AI ANALYSIS 🚀", height=55, font=("Arial", 16, "bold"), command=self.run_analysis)
        self.analyze_btn.grid(row=2, column=0, pady=20, sticky="ew")

        # label for output
        # this is the title text above the box where the ai result is shown
        self.out_lbl = ctk.CTkLabel(self.main_area, text="AI ANALYSIS REPORT", font=("Arial", 13, "bold"), text_color="#74c0fc")
        self.out_lbl.grid(row=3, column=0, sticky="w", pady=(10, 5))

        # textbox where ai result is shown
        # this box is read-only — the user cannot type here, only read the ai report
        self.output_box = ctk.CTkTextbox(self.main_area, font=("Segoe UI", 15), fg_color="#495057", border_width=1)
        self.output_box.grid(row=4, column=0, sticky="nsew", pady=(0, 10))
        self.output_box.configure(state="disabled")

        # run analysis with shift + enter
        # this connects the keyboard shortcut to the same function as the button
        self.bind("<Shift-Return>", lambda e: self.run_analysis())

    # clear both input and output
    def clear_all(self):
        # delete all text from the code input box
        self.input_box.delete("1.0", "end")
        self.update_output_box("") # clears output box

    # copy output text to clipboard
    def copy_report(self):
        # get all the text from the output box
        content = self.output_box.get("1.0", "end-1c")
        # only copy if there is real content (not an error message)
        if content and "ERROR" not in content:
            pyperclip.copy(content)
            messagebox.showinfo("Success", "Report copied to clipboard!")

    # update output box safely
    def update_output_box(self, text, color="#f8f9fa"):
        # we must unlock the box before writing to it, then lock it again after
        self.output_box.configure(state="normal")
        self.output_box.delete("1.0", "end")
        self.output_box.insert("1.0", text)
        self.output_box.configure(text_color=color)
        self.output_box.configure(state="disabled")

    # main function to run ai analysis
    def run_analysis(self):
        # get the code the user typed and remove extra spaces at the edges
        code = self.input_box.get("1.0", "end-1c").strip()
        # get the language the user selected from the dropdown
        lang = self.lang_menu.get()

        # if no code, do nothing
        if not code:
            return

        # disable button while ai works
        # this stops the user from clicking the button again while waiting
        self.analyze_btn.configure(text="AI IS THINKING...", state="disabled")
        self.update_output_box("Analyzing your code, please wait...")
        self.update()

        # create prompt for ai
        # this is the message we send to google ai, telling it how to review the code
        prompt = f"Professional {lang} review. Simple B1 English. Style, Efficiency, Bugs, Final Code.\n\nCode:\n{code}"

        success = False

        # try 5 times if error happens because
        # sometimes the ai server is busy, so we try again a few times before giving up
        for i in range(5):
            try:
                response = client.models.generate_content(model='gemini-flash-latest', contents=prompt)
                # show result
                self.update_output_box(f"--- {lang} REPORT ---\n\n" + response.text, color="#f8f9fa")
                success = True
                break
            except Exception as e:
                error_str = str(e)
                # retry if server is busy
                if "503" in error_str or "UNAVAILABLE" in error_str:
                    self.update_output_box(f"⚠️ SERVER BUSY (503). Retrying... ({i+1}/5)", color="#ffcc00")
                    self.update()
                    time.sleep(5)
                else:
                    # show other errors
                    self.update_output_box(f"❌ ERROR: {error_str}", color="#ff6b6b")
                    break

        # final error if all retries fail
        # if we tried 5 times and still failed, show this final message to the user
        if not success and "ERROR" not in self.output_box.get("1.0", "end"):
            self.update_output_box("❌ SERVER ERROR: The server is too busy right now. Please try again later.", color="#ff6b6b")

        # enable button again
        # the button becomes clickable again after the ai finishes (or fails)
        self.analyze_btn.configure(text="RUN AI ANALYSIS", state="normal")

# start the program
if __name__ == "__main__":
    # create the app and open the window
    app = ModernCodeReviewer()
    app.mainloop()