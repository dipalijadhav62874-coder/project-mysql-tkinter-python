import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector


# =========================================================
# MYSQL CONNECTION
# =========================================================

def connect_db():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456789",
            database="student_result"
        )
        return db
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", str(e))
        return None


# =========================================================
# LOGIN
# =========================================================

def login():
    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if username == "admin" and password == "1234":
        login_window.destroy()
        open_dashboard()
    else:
        messagebox.showerror(
            "Login Failed",
            "Invalid Username or Password"
        )


# =========================================================
# CLEAR FORM
# =========================================================

def clear_form():
    roll_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    class_entry.delete(0, tk.END)

    for entry in subject_entries:
        entry.delete(0, tk.END)

    total_entry.delete(0, tk.END)
    percentage_entry.delete(0, tk.END)
    grade_entry.delete(0, tk.END)


# =========================================================
# CALCULATE RESULT
# =========================================================

def calculate_result():
    try:
        marks = []

        for entry in subject_entries:
            value = int(entry.get())

            if value < 0 or value > 100:
                messagebox.showerror(
                    "Invalid Marks",
                    "Marks must be between 0 and 100."
                )
                return

            marks.append(value)

        total = sum(marks)
        percentage = total / 5

        if percentage >= 90:
            grade = "A+"
        elif percentage >= 80:
            grade = "A"
        elif percentage >= 70:
            grade = "B"
        elif percentage >= 60:
            grade = "C"
        elif percentage >= 50:
            grade = "D"
        else:
            grade = "F"

        total_entry.delete(0, tk.END)
        total_entry.insert(0, str(total))

        percentage_entry.delete(0, tk.END)
        percentage_entry.insert(0, f"{percentage:.2f}")

        grade_entry.delete(0, tk.END)
        grade_entry.insert(0, grade)

    except ValueError:
        messagebox.showerror(
            "Error",
            "Please enter valid marks."
        )


# =========================================================
# ADD RESULT
# =========================================================

def add_result():
    if (
        roll_entry.get().strip() == "" or
        name_entry.get().strip() == "" or
        class_entry.get().strip() == ""
    ):
        messagebox.showwarning(
            "Missing Data",
            "Please enter Roll No, Name and Class."
        )
        return

    calculate_result()

    if total_entry.get() == "":
        return

    db = connect_db()

    if db is None:
        return

    try:
        cursor = db.cursor()

        query = """
        INSERT INTO students
        (
            roll_no,
            student_name,
            class,
            subject1,
            subject2,
            subject3,
            subject4,
            subject5,
            total,
            percentage,
            grade
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        values = (
            roll_entry.get(),
            name_entry.get(),
            class_entry.get(),
            int(subject_entries[0].get()),
            int(subject_entries[1].get()),
            int(subject_entries[2].get()),
            int(subject_entries[3].get()),
            int(subject_entries[4].get()),
            int(total_entry.get()),
            float(percentage_entry.get()),
            grade_entry.get()
        )

        cursor.execute(query, values)
        db.commit()

        messagebox.showinfo(
            "Success",
            "Student Result Added Successfully!"
        )

        clear_form()

        cursor.close()
        db.close()

        view_records()

    except mysql.connector.Error as e:
        messagebox.showerror(
            "Database Error",
            str(e)
        )


# =========================================================
# VIEW RECORDS
# =========================================================

def view_records():
    for item in tree.get_children():
        tree.delete(item)

    db = connect_db()

    if db is None:
        return

    try:
        cursor = db.cursor()

        cursor.execute("SELECT * FROM students")

        records = cursor.fetchall()

        for record in records:
            tree.insert("", tk.END, values=record)

        cursor.close()
        db.close()

    except mysql.connector.Error as e:
        messagebox.showerror(
            "Database Error",
            str(e)
        )


# =========================================================
# SEARCH
# =========================================================

def search_result():
    search_value = search_entry.get().strip()

    if search_value == "":
        view_records()
        return

    for item in tree.get_children():
        tree.delete(item)

    db = connect_db()

    if db is None:
        return

    try:
        cursor = db.cursor()

        query = """
        SELECT * FROM students
        WHERE roll_no LIKE %s
        OR student_name LIKE %s
        """

        value = "%" + search_value + "%"

        cursor.execute(
            query,
            (value, value)
        )

        records = cursor.fetchall()

        for record in records:
            tree.insert("", tk.END, values=record)

        cursor.close()
        db.close()

    except mysql.connector.Error as e:
        messagebox.showerror(
            "Database Error",
            str(e)
        )


# =========================================================
# SELECT RECORD
# =========================================================

def select_record(event):
    selected = tree.focus()

    if selected == "":
        return

    values = tree.item(selected, "values")

    if not values:
        return

    clear_form()

    roll_entry.insert(0, values[1])
    name_entry.insert(0, values[2])
    class_entry.insert(0, values[3])

    for i in range(5):
        subject_entries[i].insert(0, values[4 + i])

    total_entry.insert(0, values[9])
    percentage_entry.insert(0, values[10])
    grade_entry.insert(0, values[11])


# =========================================================
# UPDATE RESULT
# =========================================================

def update_result():
    selected = tree.focus()

    if selected == "":
        messagebox.showwarning(
            "Select Record",
            "Please select a student record first."
        )
        return

    values = tree.item(selected, "values")

    edit_window = tk.Toplevel(dashboard)
    edit_window.title("Update Student Result")
    edit_window.geometry("500x650")

    tk.Label(
        edit_window,
        text="UPDATE STUDENT RESULT",
        font=("Arial", 18, "bold")
    ).pack(pady=15)

    form = tk.Frame(edit_window)
    form.pack()

    entries = []

    labels = [
        "Roll No",
        "Student Name",
        "Class",
        "Subject 1",
        "Subject 2",
        "Subject 3",
        "Subject 4",
        "Subject 5"
    ]

    for i, label in enumerate(labels):
        tk.Label(
            form,
            text=label
        ).grid(row=i, column=0, padx=10, pady=7)

        entry = tk.Entry(form)
        entry.grid(row=i, column=1, padx=10, pady=7)

        entry.insert(0, values[i + 1])
        entries.append(entry)

    def save_update():

        try:
            roll_no = entries[0].get().strip()
            student_name = entries[1].get().strip()
            student_class = entries[2].get().strip()

            marks = []

            for i in range(3, 8):
                mark = int(entries[i].get())

                if mark < 0 or mark > 100:
                    messagebox.showerror(
                        "Invalid Marks",
                        "Marks must be between 0 and 100."
                    )
                    return

                marks.append(mark)

            if roll_no == "" or student_name == "" or student_class == "":
                messagebox.showwarning(
                    "Missing Data",
                    "Please fill all details."
                )
                return

            total = sum(marks)
            percentage = total / 5

            if percentage >= 90:
                grade = "A+"
            elif percentage >= 80:
                grade = "A"
            elif percentage >= 70:
                grade = "B"
            elif percentage >= 60:
                grade = "C"
            elif percentage >= 50:
                grade = "D"
            else:
                grade = "F"

            db = connect_db()

            if db is None:
                return

            cursor = db.cursor()

            query = """
            UPDATE students
            SET
                roll_no=%s,
                student_name=%s,
                class=%s,
                subject1=%s,
                subject2=%s,
                subject3=%s,
                subject4=%s,
                subject5=%s,
                total=%s,
                percentage=%s,
                grade=%s
            WHERE id=%s
            """

            data = (
                roll_no,
                student_name,
                student_class,
                marks[0],
                marks[1],
                marks[2],
                marks[3],
                marks[4],
                total,
                percentage,
                grade,
                values[0]
            )

            cursor.execute(query, data)
            db.commit()

            cursor.close()
            db.close()

            messagebox.showinfo(
                "Success",
                "Student Result Updated Successfully!"
            )

            edit_window.destroy()
            view_records()

        except ValueError:
            messagebox.showerror(
                "Error",
                "Please enter valid marks."
            )

        except mysql.connector.Error as e:
            messagebox.showerror(
                "Database Error",
                str(e)
            )

    tk.Button(
        edit_window,
        text="UPDATE",
        width=15,
        height=2,
        command=save_update
    ).pack(pady=20)


# =========================================================
# DELETE RESULT
# =========================================================

def delete_result():
    selected = tree.focus()

    if selected == "":
        messagebox.showwarning(
            "Select Record",
            "Please select a record first."
        )
        return

    values = tree.item(selected, "values")

    answer = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete this record?"
    )

    if not answer:
        return

    db = connect_db()

    if db is None:
        return

    try:
        cursor = db.cursor()

        cursor.execute(
            "DELETE FROM students WHERE id=%s",
            (values[0],)
        )

        db.commit()

        messagebox.showinfo(
            "Success",
            "Record Deleted Successfully!"
        )

        cursor.close()
        db.close()

        clear_form()
        view_records()

    except mysql.connector.Error as e:
        messagebox.showerror(
            "Database Error",
            str(e)
        )


# =========================================================
# LOGOUT
# =========================================================

def logout():
    answer = messagebox.askyesno(
        "Logout",
        "Do you want to logout?"
    )

    if answer:
        dashboard.destroy()
        create_login()


# =========================================================
# ADD RESULT WINDOW
# =========================================================

def open_add_window():
    global roll_entry
    global name_entry
    global class_entry
    global subject_entries
    global total_entry
    global percentage_entry
    global grade_entry

    window = tk.Toplevel(dashboard)
    window.title("Add Student Result")
    window.geometry("500x650")

    tk.Label(
        window,
        text="ADD STUDENT RESULT",
        font=("Arial", 18, "bold")
    ).pack(pady=15)

    form = tk.Frame(window)
    form.pack()

    tk.Label(form, text="Roll No").grid(row=0, column=0, padx=10, pady=7)
    roll_entry = tk.Entry(form)
    roll_entry.grid(row=0, column=1)

    tk.Label(form, text="Student Name").grid(row=1, column=0, padx=10, pady=7)
    name_entry = tk.Entry(form)
    name_entry.grid(row=1, column=1)

    tk.Label(form, text="Class").grid(row=2, column=0, padx=10, pady=7)
    class_entry = tk.Entry(form)
    class_entry.grid(row=2, column=1)

    subject_entries = []

    for i in range(5):
        tk.Label(
            form,
            text=f"Subject {i + 1}"
        ).grid(row=i + 3, column=0, padx=10, pady=7)

        entry = tk.Entry(form)
        entry.grid(row=i + 3, column=1)

        subject_entries.append(entry)

    tk.Label(form, text="Total").grid(row=8, column=0, padx=10, pady=7)
    total_entry = tk.Entry(form)
    total_entry.grid(row=8, column=1)

    tk.Label(form, text="Percentage").grid(row=9, column=0, padx=10, pady=7)
    percentage_entry = tk.Entry(form)
    percentage_entry.grid(row=9, column=1)

    tk.Label(form, text="Grade").grid(row=10, column=0, padx=10, pady=7)
    grade_entry = tk.Entry(form)
    grade_entry.grid(row=10, column=1)

    buttons = tk.Frame(window)
    buttons.pack(pady=20)

    tk.Button(
        buttons,
        text="Calculate",
        width=12,
        command=calculate_result
    ).grid(row=0, column=0, padx=5)

    tk.Button(
        buttons,
        text="Save",
        width=12,
        command=add_result
    ).grid(row=0, column=1, padx=5)

    tk.Button(
        buttons,
        text="Clear",
        width=12,
        command=clear_form
    ).grid(row=0, column=2, padx=5)


# =========================================================
# VIEW WINDOW
# =========================================================

def open_view_window():
    global tree
    global search_entry

    window = tk.Toplevel(dashboard)
    window.title("Student Results")
    window.geometry("1200x600")

    tk.Label(
        window,
        text="STUDENT RESULTS",
        font=("Arial", 18, "bold")
    ).pack(pady=10)

    search_frame = tk.Frame(window)
    search_frame.pack(pady=5)

    tk.Label(
        search_frame,
        text="Search"
    ).pack(side=tk.LEFT)

    search_entry = tk.Entry(
        search_frame,
        width=30
    )
    search_entry.pack(side=tk.LEFT, padx=10)

    tk.Button(
        search_frame,
        text="Search",
        command=search_result
    ).pack(side=tk.LEFT)

    columns = (
        "ID",
        "Roll No",
        "Name",
        "Class",
        "Sub1",
        "Sub2",
        "Sub3",
        "Sub4",
        "Sub5",
        "Total",
        "Percentage",
        "Grade"
    )

    tree = ttk.Treeview(
        window,
        columns=columns,
        show="headings"
    )

    for column in columns:
        tree.heading(column, text=column)
        tree.column(column, width=90)

    tree.pack(
        fill=tk.BOTH,
        expand=True,
        padx=10,
        pady=10
    )

    tree.bind(
        "<ButtonRelease-1>",
        select_record
    )

    button_frame = tk.Frame(window)
    button_frame.pack(pady=10)

    tk.Button(
        button_frame,
        text="Update Selected",
        command=update_result
    ).pack(side=tk.LEFT, padx=5)

    tk.Button(
        button_frame,
        text="Delete Selected",
        command=delete_result
    ).pack(side=tk.LEFT, padx=5)

    tk.Button(
        button_frame,
        text="Refresh",
        command=view_records
    ).pack(side=tk.LEFT, padx=5)

    view_records()


# =========================================================
# DASHBOARD
# =========================================================

def open_dashboard():
    global dashboard

    dashboard = tk.Tk()
    dashboard.title("Student Result Management System")
    dashboard.geometry("650x500")

    tk.Label(
        dashboard,
        text="STUDENT RESULT MANAGEMENT SYSTEM",
        font=("Arial", 20, "bold")
    ).pack(pady=30)

    tk.Button(
        dashboard,
        text="Add Result",
        width=25,
        height=2,
        command=open_add_window
    ).pack(pady=8)

    tk.Button(
        dashboard,
        text="View / Search / Update / Delete",
        width=25,
        height=2,
        command=open_view_window
    ).pack(pady=8)

    tk.Button(
        dashboard,
        text="Logout",
        width=25,
        height=2,
        command=logout
    ).pack(pady=8)

    dashboard.mainloop()


# =========================================================
# LOGIN WINDOW
# =========================================================

def create_login():
    global login_window
    global username_entry
    global password_entry

    login_window = tk.Tk()
    login_window.title("Login - Student Result Management System")
    login_window.geometry("500x400")

    tk.Label(
        login_window,
        text="STUDENT RESULT MANAGEMENT SYSTEM",
        font=("Arial", 17, "bold")
    ).pack(pady=35)

    tk.Label(
        login_window,
        text="Username",
        font=("Arial", 12)
    ).pack()

    username_entry = tk.Entry(
        login_window,
        width=30
    )
    username_entry.pack(pady=8)

    tk.Label(
        login_window,
        text="Password",
        font=("Arial", 12)
    ).pack()

    password_entry = tk.Entry(
        login_window,
        width=30,
        show="*"
    )
    password_entry.pack(pady=8)

    tk.Button(
        login_window,
        text="LOGIN",
        width=20,
        height=2,
        command=login
    ).pack(pady=25)

    login_window.mainloop()


# =========================================================
# START PROGRAM
# =========================================================

create_login()