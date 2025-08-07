import tkinter as tk
from tkinter import messagebox
import pandas as pd

# Try to read the records from CSV, otherwise create a new empty DataFrame
try:
    df = pd.read_csv('./records.csv')
except Exception as e:
    data = {
        "Date": [],
        "Description": [],
        "Amount": [],
        "Type": []
    }
    df = pd.DataFrame(data)

# Main application class
class BudgetTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Budget Tracker")

        # --- Input Form Section ---

        # Date input
        self.label_date = tk.Label(root, text="Date (YY-MM-DD):")
        self.label_date.grid(row=0, column=0)
        self.entry_date = tk.Entry(root)
        self.entry_date.grid(row=0, column=1)

        # Description input
        self.label_description = tk.Label(root, text="Description:")
        self.label_description.grid(row=1, column=0)
        self.entry_description = tk.Entry(root)
        self.entry_description.grid(row=1, column=1)

        # Amount input
        self.label_amount = tk.Label(root, text="Amount:")
        self.label_amount.grid(row=2, column=0)
        self.entry_amount = tk.Entry(root)
        self.entry_amount.grid(row=2, column=1)

        # Type input (Income/Expense)
        self.label_type = tk.Label(root, text="Type (Income/Expense):")
        self.label_type.grid(row=3, column=0)
        self.entry_type = tk.Entry(root)
        self.entry_type.grid(row=3, column=1)

        # Add Entry button
        self.button_add = tk.Button(root, text="Add Entry", command=self.add_entry)
        self.button_add.grid(row=4, column=0, columnspan=2)

        # View Entries button
        self.button_view = tk.Button(root, text="View Entries", command=self.view_entries)
        self.button_view.grid(row=5, column=0, columnspan=2)

        # Search Entries button
        self.button_search = tk.Button(root, text="Search Entries", command=self.search_entries)
        self.button_search.grid(row=6, column=0, columnspan=2)

        # Monthly Summary button
        self.button_summary = tk.Button(root, text="Monthly Summary", command=self.monthly_summary)
        self.button_summary.grid(row=7, column=0, columnspan=2)

    # --- Monthly Summary Window ---
    def monthly_summary(self):
        global df
        summary_top = tk.Toplevel(self.root)
        summary_top.title("Monthly Summary")

        text = tk.Text(summary_top)
        text.pack()

        report_df = df.copy()

        # Extracting month from Date
        report_df['Month'] = report_df['Date'].str.split('-').str[1].str.strip()

        # Convert Amount to numeric to avoid errors in calculations
        report_df['Amount'] = pd.to_numeric(report_df['Amount'], errors='coerce')

        # Group by Month and Type
        monthly_income = report_df.query("Type == 'Income'").groupby("Month")['Amount'].sum()
        monthly_expense = report_df.query("Type == 'Expense'").groupby("Month")['Amount'].sum()

        # Create summary table
        summary_df = pd.DataFrame({
            "Income": monthly_income,
            "Expense": monthly_expense
        }).fillna(0)

        # Calculate Savings
        summary_df['Savings'] = summary_df['Income'] - summary_df['Expense']

        # Show summary in text box
        text.insert(tk.END, summary_df.to_string())

    # --- Search Function ---
    def search_entries(self):
        global df
        search_top = tk.Toplevel(self.root)
        search_top.title("Search Entries")

        search_label = tk.Label(search_top, text="Enter search criteria:")
        search_label.pack()

        self.search_entry = tk.Entry(search_top)
        self.search_entry.pack()

        search_button = tk.Button(search_top, text="Search", command=self.perform_search)
        search_button.pack()

    def perform_search(self):
        global df
        search_term = self.search_entry.get().lower()

        # Filter DataFrame based on search term in Date or Description
        filtered_df = df[df['Date'].str.lower().str.contains(search_term) | df['Description'].str.lower().str.contains(search_term)]

        # Create results window
        results_top = tk.Toplevel(self.root)
        results_top.title("Search Results")

        text = tk.Text(results_top)
        text.pack()

        # Show each matching entry
        for index, row in filtered_df.iterrows():
            text.insert(tk.END, f"Date: {row['Date']} | Desription: {row['Description']} | Amount: {row['Amount']} | Type: {row['Type']} \n\n")

    # --- Add Entry Function ---
    def add_entry(self):
        # Get data from form
        date = self.entry_date.get()
        description = self.entry_description.get()
        amount = self.entry_amount.get()
        entry_type = self.entry_type.get()

        # Ensure all fields are filled
        if date and description and amount and entry_type:
            new_entry = pd.DataFrame({
                "Date": [date],
                "Description": [description],
                "Amount": [amount],
                "Type": [entry_type]
            })

            global df 
            df = pd.concat([df, new_entry], ignore_index=True)
            df.to_csv('./records.csv', index=False)

            messagebox.showinfo("Success", "Entry saved successfully!")

            # Clear input fields
            self.entry_date.delete(0, tk.END)
            self.entry_description.delete(0, tk.END)
            self.entry_amount.delete(0, tk.END)
            self.entry_type.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "All fields are required.")

    # --- View Entries Function ---
    def view_entries(self):
        global df
        self.top = tk.Toplevel(self.root)
        self.top.title("View Entries")

        text = tk.Text(self.top)
        text.pack()

        # Show each entry
        for index, row in df.iterrows():
            text.insert(tk.END, f"Date: {row['Date']} | Description: {row['Description']} | Amount: {row['Amount']} | Type: {row['Type']}\n")

            # Edit and Delete buttons for each entry
            edit_button = tk.Button(self.top, text="Edit", command=lambda i=index: self.edit_entry(i))
            delete_button = tk.Button(self.top, text="Delete", command=lambda i=index: self.delete_entry(i))
            text.window_create(tk.END, window=edit_button)
            text.window_create(tk.END, window=delete_button)
            text.insert(tk.END, "\n\n")

    # --- Edit Entry ---
    def edit_entry(self, index):
        global df
        self.edit_top = tk.Toplevel(self.root)
        self.edit_top.title("Edit Entry")

        # Pre-fill the entry form with existing values
        self.edit_date = tk.Entry(self.edit_top)
        self.edit_date.insert(0, df.at[index, 'Date'])
        self.edit_date.pack()
        
        self.edit_description = tk.Entry(self.edit_top)
        self.edit_description.insert(0, df.at[index, 'Description'])
        self.edit_description.pack()

        self.edit_amount = tk.Entry(self.edit_top)
        self.edit_amount.insert(0, df.at[index, 'Amount'])
        self.edit_amount.pack()

        self.edit_type = tk.Entry(self.edit_top)
        self.edit_type.insert(0, df.at[index, 'Type'])
        self.edit_type.pack()

        save_button = tk.Button(self.edit_top, text="Save", command=lambda i=index: self.save_edit(i))
        save_button.pack()

    def save_edit(self, index):
        global df
        # Save the edited values
        df.at[index, 'Date'] = self.edit_date.get()
        df.at[index, 'Description'] = self.edit_description.get()
        df.at[index, 'Amount'] = self.edit_amount.get()
        df.at[index, 'Type'] = self.edit_type.get()
        df.to_csv('./records.csv', index=False)

        messagebox.showinfo("Success", "Entry updated successfully")
        self.edit_top.destroy()
        self.top.destroy()
        self.view_entries()

    # --- Delete Entry ---
    def delete_entry(self, index):
        global df
        df = df.drop(df.index[index])  # Remove the row
        df.reset_index(drop=True, inplace=True)  # Reset index
        df.to_csv('./records.csv', index=False)

        messagebox.showinfo("Success", "Entry deleted successfully!")
        self.top.destroy()
        self.view_entries()

# --- Launch the App ---
root = tk.Tk()
app = BudgetTrackerApp(root)
root.mainloop()



