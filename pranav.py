import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# Database Initialization
def init_db():
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()

    # Create tables if they do not exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      price REAL NOT NULL,
                      stock INTEGER NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      customer TEXT NOT NULL,
                      items TEXT NOT NULL,
                      total_price REAL NOT NULL)''')

    conn.commit()
    conn.close()

init_db()

# Function to add a product (Admin)
def add_product():
    name = product_name_entry.get().strip()
    price = product_price_entry.get().strip()
    stock = product_stock_entry.get().strip()

    if name and price and stock:
        try:
            price = float(price)
            stock = int(stock)

            conn = sqlite3.connect("grocery.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", (name, price, stock))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Product '{name}' added successfully!")
            product_name_entry.delete(0, tk.END)
            product_price_entry.delete(0, tk.END)
            product_stock_entry.delete(0, tk.END)
            fetch_products()  # Refresh product list

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for price and stock")
    else:
        messagebox.showerror("Error", "Please fill all fields")

# Function to fetch available products (for Customer)
def fetch_products():
    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, stock FROM products WHERE stock > 0")
    products = cursor.fetchall()
    conn.close()

    product_list.delete(*product_list.get_children())  # Clear previous data
    for product in products:
        product_list.insert("", tk.END, values=product)

# Function to place an order (Customer)
def place_order():
    selected_item = product_list.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a product to order")
        return

    product_id = product_list.item(selected_item, "values")[0]
    quantity = quantity_entry.get().strip()

    if not quantity.isdigit() or int(quantity) <= 0:
        messagebox.showerror("Error", "Enter a valid quantity")
        return

    quantity = int(quantity)

    conn = sqlite3.connect("grocery.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name, price, stock FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()

    if not product or quantity > product[2]:
        messagebox.showerror("Error", "Insufficient stock")
        conn.close()
        return

    total_price = product[1] * quantity

    cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (quantity, product_id))

    cursor.execute("INSERT INTO orders (customer, items, total_price) VALUES (?, ?, ?)",
                   ("Customer", f"{product[0]} x {quantity}", total_price))

    conn.commit()
    conn.close()

    messagebox.showinfo("Success", f"Order placed successfully for {product[0]} (x{quantity})")
    fetch_products()  # Refresh product list

# GUI Setup for Admin Panel (Adding Products)
admin_root = tk.Tk()
admin_root.title("Admin - Add Products")
admin_root.geometry("400x300")

tk.Label(admin_root, text="Product Name:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
product_name_entry = tk.Entry(admin_root)
product_name_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(admin_root, text="Price ($):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
product_price_entry = tk.Entry(admin_root)
product_price_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(admin_root, text="Stock:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
product_stock_entry = tk.Entry(admin_root)
product_stock_entry.grid(row=2, column=1, padx=10, pady=5)

tk.Button(admin_root, text="Add Product", command=add_product, bg="green", fg="white").grid(row=3, column=1, padx=10, pady=10)

# GUI Setup for Customer Panel (Placing Orders)
customer_root = tk.Toplevel(admin_root)
customer_root.title("Customer - Order Products")
customer_root.geometry("500x400")

tk.Label(customer_root, text="Available Products", font=("Arial", 14)).pack(pady=10)

columns = ("ID", "Name", "Price", "Stock")
product_list = ttk.Treeview(customer_root, columns=columns, show="headings")
for col in columns:
    product_list.heading(col, text=col)
product_list.pack()

tk.Label(customer_root, text="Quantity:").pack(pady=5)
quantity_entry = tk.Entry(customer_root)
quantity_entry.pack()

tk.Button(customer_root, text="Place Order", command=place_order, bg="blue", fg="white").pack(pady=10)

fetch_products()
admin_root.mainloop()
