
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import date

# MySQL Database Connection
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin1234",
        database="food_waste_tracker"
    )

# Add Food Item
def add_food():
    name = name_entry.get()
    quantity = quantity_entry.get()
    price = price_entry.get()
    expiry = expiry_entry.get()

    if not name or not quantity or not price or not expiry:
        messagebox.showwarning("Warning", "Please fill all fields")
        return

    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO food_items (item_name, quantity, price, expiry_date) VALUES (%s, %s, %s, %s)",
            (name, int(quantity), float(price), expiry)
        )

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Food item added successfully!")
        clear_fields()
        view_food()

    except Exception as e:
        messagebox.showerror("Database Error", str(e))


# View Food Items
def view_food():
    for row in tree.get_children():
        tree.delete(row)

    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM food_items")
        rows = cursor.fetchall()

        for row in rows:
            tree.insert("", tk.END, values=row)

        conn.close()

    except Exception as e:
        messagebox.showerror("Database Error", str(e))


# Update Food Item
def update_food():
    selected = tree.focus()

    if not selected:
        messagebox.showwarning("Warning", "Select a food item first")
        return

    item_id = tree.item(selected)["values"][0]

    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            """UPDATE food_items
               SET item_name=%s, quantity=%s, price=%s, expiry_date=%s
               WHERE item_id=%s""",
            (
                name_entry.get(),
                int(quantity_entry.get()),
                float(price_entry.get()),
                expiry_entry.get(),
                item_id
            )
        )

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Food item updated!")
        clear_fields()
        view_food()

    except Exception as e:
        messagebox.showerror("Error", str(e))


# Delete Food Item
def delete_food():
    selected = tree.focus()

    if not selected:
        messagebox.showwarning("Warning", "Select a food item first")
        return

    item_id = tree.item(selected)["values"][0]

    if not messagebox.askyesno("Confirm", "Delete this food item?"):
        return

    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM food_items WHERE item_id=%s",
            (item_id,)
        )

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Food item deleted!")
        clear_fields()
        view_food()

    except Exception as e:
        messagebox.showerror("Error", str(e))


# Expiry Status
def check_expiry():
    for row in tree.get_children():
        tree.delete(row)

    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT item_id, item_name, quantity, price, expiry_date,
            CASE
                WHEN expiry_date < CURDATE() THEN 'EXPIRED'
                WHEN expiry_date <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)
                    THEN 'EXPIRING SOON'
                ELSE 'FRESH'
            END
            FROM food_items
        """)

        rows = cursor.fetchall()

        for row in rows:
            tree.insert("", tk.END, values=row)

        conn.close()

    except Exception as e:
        messagebox.showerror("Error", str(e))


# Select Table Row
def select_item(event):
    selected = tree.focus()

    if selected:
        values = tree.item(selected)["values"]

        name_entry.delete(0, tk.END)
        name_entry.insert(0, values[1])

        quantity_entry.delete(0, tk.END)
        quantity_entry.insert(0, values[2])

        price_entry.delete(0, tk.END)
        price_entry.insert(0, values[3])

        expiry_entry.delete(0, tk.END)
        expiry_entry.insert(0, str(values[4]))


# Clear Input Fields
def clear_fields():
    name_entry.delete(0, tk.END)
    quantity_entry.delete(0, tk.END)
    price_entry.delete(0, tk.END)
    expiry_entry.delete(0, tk.END)


# Main Window
root = tk.Tk()
root.title("Smart Food Waste & Expiry Tracker")
root.geometry("950x600")
root.configure(bg="#eef2f3")

title = tk.Label(
    root,
    text="Smart Food Waste & Expiry Tracker",
    font=("Arial", 22, "bold"),
    bg="#eef2f3",
    fg="#17365d"
)
title.pack(pady=15)

# Input Frame
form = tk.Frame(root, bg="#eef2f3")
form.pack(pady=10)

tk.Label(form, text="Food Name", bg="#eef2f3").grid(row=0, column=0, padx=8)
tk.Label(form, text="Quantity", bg="#eef2f3").grid(row=0, column=1, padx=8)
tk.Label(form, text="Price", bg="#eef2f3").grid(row=0, column=2, padx=8)
tk.Label(form, text="Expiry Date (YYYY-MM-DD)", bg="#eef2f3").grid(row=0, column=3, padx=8)

name_entry = tk.Entry(form, width=15)
quantity_entry = tk.Entry(form, width=12)
price_entry = tk.Entry(form, width=12)
expiry_entry = tk.Entry(form, width=18)

name_entry.grid(row=1, column=0, padx=8, pady=8)
quantity_entry.grid(row=1, column=1, padx=8, pady=8)
price_entry.grid(row=1, column=2, padx=8, pady=8)
expiry_entry.grid(row=1, column=3, padx=8, pady=8)

# Buttons
buttons = tk.Frame(root, bg="#eef2f3")
buttons.pack(pady=10)

tk.Button(buttons, text="Add Food", width=14, command=add_food).grid(row=0, column=0, padx=5)
tk.Button(buttons, text="View Food", width=14, command=view_food).grid(row=0, column=1, padx=5)
tk.Button(buttons, text="Update Food", width=14, command=update_food).grid(row=0, column=2, padx=5)
tk.Button(buttons, text="Delete Food", width=14, command=delete_food).grid(row=0, column=3, padx=5)
tk.Button(buttons, text="Check Expiry", width=14, command=check_expiry).grid(row=0, column=4, padx=5)
tk.Button(buttons, text="Clear", width=10, command=clear_fields).grid(row=0, column=5, padx=5)

# Data Table
columns = ("ID", "Name", "Quantity", "Price", "Expiry Date", "Status")

tree = ttk.Treeview(root, columns=columns, show="headings", height=15)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=135)

tree.pack(pady=20, padx=15, fill="x")
tree.bind("<<TreeviewSelect>>", select_item)

view_food()

root.mainloop()
