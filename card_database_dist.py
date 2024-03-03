import sqlite3
from tkinter import *
from tkinter import Label, Tk, font, Button, Entry, Toplevel


# Create a database connection
conn = sqlite3.connect("card_database.db")
c = conn.cursor()

# Create a table to store the data
c.execute(
    """CREATE TABLE IF NOT EXISTS card_database
             (number INTEGER, name TEXT, owned BOOLEAN)"""
)


# Function to insert data into the table
def insert_data(number, name, owned):
    c.execute("INSERT INTO card_database VALUES (?, ?, ?)", (number, name, owned))
    conn.commit()


# Function to retrieve data from the table
def get_data():
    c.execute("SELECT * FROM card_database")
    return c.fetchall()


# Function to filter data based on number, name, and owned status
def filter_data(number=None, name=None, owned=None):
    query = "SELECT * FROM card_database WHERE"
    conditions = []
    if number is not None:
        conditions.append(f"number = {number}")
    if name is not None:
        conditions.append(f"name = '{name}'")
    if owned is not None:
        conditions.append(f"owned = {owned}")
    query += " AND ".join(conditions)
    c.execute(query)
    return c.fetchall()


# Create a GUI window
window = Tk()
window.title("card_database Database")
window.configure(bg="black")
font = font.Font(family="Calibri", size=12, weight="bold")


# Function to search the database
def search():
    # Get the search values from the entry fields
    number = number_entry.get()
    name = name_entry.get()
    owned = owned_var.get()

    # Determine which field is filled and execute the appropriate query
    if number:
        c.execute(
            "SELECT * FROM card_database WHERE number = ? ORDER BY number", (number,)
        )
    elif name:
        c.execute(
            "SELECT * FROM card_database WHERE name LIKE ? ORDER BY number",
            ("%" + name + "%",),
        )
    elif owned:
        c.execute(
            "SELECT * FROM card_database WHERE owned = ? ORDER BY number", (owned,)
        )
    elif not number and not name and not owned:
        c.execute("SELECT * FROM card_database")

    rows = c.fetchall()
    rows.sort(key=lambda x: x[0])

    # DEBUG
    # Print out the contents of the listbox
    # for i in range(results_listbox.size()):
    #     print(results_listbox.get(i))

    # Clear the listbox
    results_listbox.delete(0, END)

    # Add the results to the listbox
    for row in rows:
        owned_status = "[x]" if row[2] else "[ ]"
        # Pad the number with leading zeros
        padded_number = str(row[0]).zfill(3)
        results_listbox.insert(END, f"{padded_number}. {row[1]} {owned_status}")

# Function to add an entry to the database
def add_entry():
    number = number_entry.get()
    name = name_entry.get()
    owned = owned_var.get()

    # Insert the values into the database
    # Assuming `conn` is a sqlite3.Connection object and `c` is a sqlite3.Cursor object
    c.execute("INSERT INTO card_database VALUES (?, ?, ?)", (number, name, owned))
    conn.commit()

    # Clear the entry fields
    number_entry.delete(0, END)
    name_entry.delete(0, END)
    owned_var.set(False)

# Function to update the values of a row
def update():
    # Get the values from the entry fields
    number = number_entry.get()
    name = name_entry.get()
    owned = owned_var.get()

    # Execute the UPDATE query
    c.execute(
        "UPDATE card_database SET name = ?, owned = ? WHERE number = ?",
        (name, owned, number),
    )

    # Commit the changes
    conn.commit()


def filter_not_owned():
    # Create a cursor
    cursor = conn.cursor()

    # Execute a query to get all rows where "owned" is 0
    cursor.execute("SELECT * FROM card_database WHERE owned = 0")

    # Fetch all rows
    rows = cursor.fetchall()

    # Close the cursor
    cursor.close()

    # Update the display with the filtered rows
    results_listbox.delete(0, END)
    for row in rows:
        results_listbox.insert(END, row)


def delete():
    # Get the number from the entry field
    number = number_entry.get()

    # Execute the DELETE query
    c.execute("DELETE FROM card_database WHERE number = ?", (number,))

    # Commit the changes
    conn.commit()


# Function to insert a new row at a specified position
def insert_at_position(number, values):
    # Create a cursor
    cursor = conn.cursor()

    try:
        # Update the "number" column of all rows with a number greater than or equal to the specified number
        cursor.execute(
            f"UPDATE card_database SET number = number + 1 WHERE number >= {number}"
        )

        # Prepare the values for the SQL query
        placeholders = ", ".join("?" for _ in values)
        query = f"INSERT INTO card_database VALUES ({number}, {placeholders})"

        # Insert the new row at the specified position
        cursor.execute(query, values)

        # Commit the transaction
        conn.commit()

    except Exception as e:
        # If an error occurred, rollback the transaction
        conn.rollback()
        print(f"An error occurred: {e}")

    finally:
        # Close the cursor
        cursor.close()
    cursor = conn.cursor()


# Function to open a new window for entering a new entry
def open_new_entry_window():
    # Create a new window
    new_entry_window = Toplevel(window)

    # Create an Entry widget for the number
    number_label = Label(new_entry_window, text="Number")
    number_label.pack()
    number_entry = Entry(new_entry_window)
    number_entry.pack()

    # Create Entry widgets for the values
    value_labels = []
    value_entries = []
    for column in ["Name", "Owned"]:
        label = Label(new_entry_window, text=column)
        label.pack()
        value_labels.append(label)

        entry = Entry(new_entry_window)
        entry.pack()
        value_entries.append(entry)

    # Create a button to submit the new entry
    submit_button = Button(
        new_entry_window,
        text="Submit",
        command=lambda: submit_new_entry(number_entry, value_entries),
    )
    submit_button.pack()


# Function to update the display
def update_display():
    # Clear the listbox
    results_listbox.delete(0, END)

    # Fetch all rows from the database
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM card_database ORDER BY number")
    rows = cursor.fetchall()
    cursor.close()

    # Insert the rows into the listbox
    for row in rows:
        results_listbox.insert(END, row)


# function to submit a new entry
def submit_new_entry(number_entry, value_entries):
    # Get the number and the values from the Entry widgets
    number = int(number_entry.get())
    values = [entry.get() for entry in value_entries]

    # Insert the new entry at the specified position
    insert_at_position(number, values)

    # Update the display
    update_display()


# Function to update the "number" column of each row -- DEBUG
def update_numbers():
    # Create a cursor
    cursor = conn.cursor()

    try:
        # Fetch all rows from the database
        cursor.execute("SELECT * FROM card_database ORDER BY number")
        rows = cursor.fetchall()

        # Update the "number" column of each row to a temporary number
        for i, row in enumerate(rows, start=1):
            cursor.execute(
                "UPDATE card_database SET number = ? WHERE name = ?",
                (i + len(rows), row[0]),
            )

        # Update the "number" column of each row to the correct number
        for i, row in enumerate(rows, start=1):
            cursor.execute(
                "UPDATE card_database SET number = ? WHERE name = ?", (i, row[0])
            )

        # Commit the transaction
        conn.commit()

    except Exception as e:
        # If an error occurred, rollback the transaction
        conn.rollback()
        print(f"An error occurred: {e}")

    finally:
        # Close the cursor
        cursor.close()


# Function to remove duplicate entries  DEBUG
def fix_duplicates():
    # Create a cursor
    cursor = conn.cursor()

    try:
        # Update the "number" column of each row where the number is greater than or equal to 88
        cursor.execute(
            "UPDATE card_database SET number = number + 1 WHERE number >= 87"
        )

        # Commit the transaction
        conn.commit()

    except Exception as e:
        # If an error occurred, rollback the transaction
        conn.rollback()
        print(f"An error occurred: {e}")

    finally:
        # Close the cursor
        cursor.close()


# Function to renumber the "number" column of each row -- DEBUG
def renumber():
    # Create a cursor
    cursor = conn.cursor()

    try:
        # Fetch all rows from the database
        cursor.execute("SELECT * FROM card_database ORDER BY number")
        rows = cursor.fetchall()

        # Update the "number" column of each row to the correct number
        for i, row in enumerate(rows, start=1):
            cursor.execute(
                "UPDATE card_database SET number = ? WHERE name = ?", (i, row[1])
            )

        # Commit the transaction
        conn.commit()

    except Exception as e:
        # If an error occurred, rollback the transaction
        conn.rollback()
        print(f"An error occurred: {e}")

    finally:
        # Close the cursor
        cursor.close()


# Create input fields and labels
number_label = Label(window, text="Number:", font=font, bg="black", fg="white")
number_label.grid()
number_entry = Entry(window)
number_entry.grid()

name_label = Label(window, text="Name:", font=font, bg="black", fg="white")
name_label.grid()
name_entry = Entry(window)
name_entry.grid()

owned_label = Label(window, text="State:", font=font, bg="black", fg="white")
owned_label.grid()
owned_var = BooleanVar()
owned_checkbox = Checkbutton(window, text="Owned", variable=owned_var)
owned_checkbox.grid()

results_listbox = Listbox(window, width=50)
results_listbox.grid(row=4, column=0, columnspan=2)

# Set the weights of the rows and columns
window.grid_columnconfigure(0, weight=1)
window.grid_rowconfigure(4, weight=1)

# Buttons
search_button = Button(
    window, text="Search", command=search, width=20, font=font, bg="black", fg="black"
)
search_button.grid()

add_button = Button(
    window, text="Add", command=add_entry, width=20, font=font, bg="black", fg="black"
)
add_button.grid()

filter_button = Button(
    window,
    text="Filter",
    command=filter_not_owned,
    width=20,
    font=font,
    bg="black",
    fg="black",
)
filter_button.grid()

update_button = Button(
    window, text="Update", command=update, width=20, font=font, bg="black", fg="black"
)
update_button.grid()

delete_button = Button(
    window, text="Delete", command=delete, width=20, font=font, bg="black", fg="black"
)
delete_button.grid()

new_entry_button = Button(
    window,
    text="Insert",
    command=open_new_entry_window,
    width=20,
    font=font,
    bg="black",
    fg="black",
)
new_entry_button.grid()

quit_button = Button(
    window,
    text="Quit",
    command=window.destroy,
    width=20,
    font=font,
    bg="black",
    fg="black",
)
quit_button.grid()

update_numbers()

renumber()
# Start the GUI event loop
window.mainloop()

# Close connection
conn.close()
