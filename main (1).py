"""
EXPENSE, ATTENDANCE, GRADING AND BILLING MANAGEMENT SYSTEM
A menu-driven Python program based on the supplied Client Requirements Specification.

Run with:
    python main.py

Only Python's standard library is used.
"""

from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import sys

# ----------------------------- CONSTANTS -----------------------------

CATEGORIES = ("Food", "Travel", "Utilities", "Stationery", "Other")
DEFAULT_SUBJECTS = ("Maths", "Science", "English", "History", "Computer")
ATTENDANCE_ELIGIBLE = 75.0
ATTENDANCE_WARNING = 60.0
PASS_MARK = 35.0
TAX_RATE = Decimal("0.18")
MONEY_PLACES = Decimal("0.01")

# All records are kept in memory for the current program session.
expenses = []
attendance_records = []
student_records = []
invoices = []


# -------------------------- INPUT VALIDATION --------------------------

def money(value):
    """Convert a number to money rounded to two decimal places."""
    return Decimal(str(value)).quantize(MONEY_PLACES, rounding=ROUND_HALF_UP)


def get_int(prompt, min_val=None, max_val=None):
    """Read and validate a whole number, asking again when it is invalid."""
    while True:
        try:
            value = int(input(prompt).strip())
            if min_val is not None and value < min_val:
                print(f"Enter a whole number of at least {min_val}.")
                continue
            if max_val is not None and value > max_val:
                print(f"Enter a whole number not greater than {max_val}.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a whole number.")
        except (EOFError, KeyboardInterrupt):
            raise


def get_float(prompt, min_val=None, max_val=None):
    """Read and validate a number, asking again when it is invalid."""
    while True:
        try:
            value = float(input(prompt).strip())
            if min_val is not None and value < min_val:
                print(f"Value must be at least {min_val}.")
                continue
            if max_val is not None and value > max_val:
                print(f"Value must not be greater than {max_val}.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a number.")
        except (EOFError, KeyboardInterrupt):
            raise


def get_money(prompt, min_val=Decimal("0.01")):
    """Read a valid monetary amount with no more than two decimal places."""
    while True:
        raw = input(prompt).strip()
        try:
            value = Decimal(raw)
            if not value.is_finite():
                print("Please enter a valid amount.")
                continue
            if value < min_val:
                print(f"Amount must be at least {min_val:.2f}.")
                continue
            if value.as_tuple().exponent < -2:
                print("Please enter an amount with no more than 2 decimal places.")
                continue
            return money(value)
        except InvalidOperation:
            print("Invalid amount. Please enter a positive number.")
        except (EOFError, KeyboardInterrupt):
            raise


def get_name(prompt):
    """Read a name containing 2 to 40 alphabetic characters and spaces."""
    while True:
        name = input(prompt).strip()
        if 2 <= len(name) <= 40 and all(ch.isalpha() or ch.isspace() for ch in name):
            if any(ch.isalpha() for ch in name):
                return " ".join(name.split())
        print("Name must contain 2-40 letters and spaces only.")


def get_text(prompt, min_len=1, max_len=60):
    """Read non-empty descriptive text within a sensible length."""
    while True:
        value = input(prompt).strip()
        if min_len <= len(value) <= max_len:
            return value
        print(f"Please enter between {min_len} and {max_len} characters.")


def get_choice(prompt, options):
    """Read a choice from a fixed list; comparison is case-insensitive."""
    lookup = {str(option).casefold(): option for option in options}
    while True:
        value = input(prompt).strip().casefold()
        if value in lookup:
            return lookup[value]
        print("Choose one of: " + ", ".join(str(x) for x in options))


def pause():
    input("\nPress Enter to return to the menu...")


def print_line(char="-", width=78):
    print(char * width)


def no_records(message="No records available."):
    print(message)


# ---------------------------- EXPENSE MODULE ---------------------------

def add_expense():
    """Add one expense after validating its description, category and amount."""
    print("\n--- ADD EXPENSE ---")
    description = get_text("Description: ", 2, 60)
    category = get_choice(
        "Category (Food / Travel / Utilities / Stationery / Other): ", CATEGORIES
    )
    amount = get_money("Amount: ")
    expenses.append({
        "description": description,
        "category": category,
        "amount": amount,
        "date": date.today().isoformat()
    })
    print("Expense added successfully!")


def view_expenses():
    """Display all expenses in aligned columns."""
    print("\n--- ALL EXPENSES ---")
    if not expenses:
        no_records("No expense records available.")
        return
    print(f"{'No.':<5}{'Description':<24}{'Category':<16}{'Amount':>12}  {'Date'}")
    print_line()
    for number, item in enumerate(expenses, 1):
        print(f"{number:<5}{item['description']:<24}{item['category']:<16}"
              f"{item['amount']:>12.2f}  {item['date']}")
    print_line()


def expense_summary():
    """Show total expense, category totals, and highest and lowest expenses."""
    print("\n--- EXPENSE SUMMARY ---")
    if not expenses:
        no_records("No expense records available.")
        return

    category_totals = {category: Decimal("0.00") for category in CATEGORIES}
    for item in expenses:
        category_totals[item["category"]] += item["amount"]

    grand_total = sum((item["amount"] for item in expenses), Decimal("0.00"))
    print(f"{'CATEGORY':<20}{'TOTAL':>15}")
    print_line()
    for category, total in category_totals.items():
        print(f"{category:<20}{total:>15.2f}")
    print_line()
    print(f"{'GRAND TOTAL':<20}{grand_total:>15.2f}")

    highest = max(expenses, key=lambda item: item["amount"])
    lowest = min(expenses, key=lambda item: item["amount"])
    print(f"Highest expense: {highest['description']} - {highest['amount']:.2f}")
    print(f"Lowest expense : {lowest['description']} - {lowest['amount']:.2f}")


def expense_menu():
    while True:
        print("\n========== EXPENSE MANAGEMENT ==========")
        print("1. Add Expense")
        print("2. View All Expenses")
        print("3. Expense Summary")
        print("4. Back to Main Menu")
        choice = get_int("Enter your choice (1-4): ", 1, 4)
        if choice == 1:
            add_expense()
        elif choice == 2:
            view_expenses()
        elif choice == 3:
            expense_summary()
        else:
            return
        pause()


# -------------------------- ATTENDANCE MODULE --------------------------

def attendance_status(percentage):
    """Return the status assigned by the attendance percentage rules."""
    if percentage >= ATTENDANCE_ELIGIBLE:
        return "Eligible"
    if percentage >= ATTENDANCE_WARNING:
        return "Warning"
    return "Shortage"


def mark_attendance():
    """Collect working days and attendance records for multiple people."""
    print("\n--- MARK ATTENDANCE ---")
    total_days = get_int("Enter total number of working days: ", 1)
    print("Enter each person's details. Type 'done' as the name to finish.")
    added = 0

    while True:
        raw_name = input("Person name (or done): ").strip()
        if raw_name.casefold() == "done":
            break
        if not (2 <= len(raw_name) <= 40 and
                all(ch.isalpha() or ch.isspace() for ch in raw_name) and
                any(ch.isalpha() for ch in raw_name)):
            print("Name must contain 2-40 letters and spaces only.")
            continue
        name = " ".join(raw_name.split())
        person_id = get_text("Person ID: ", 1, 20)
        present = get_int(f"Days present (0-{total_days}): ", 0, total_days)
        percentage = (present / total_days) * 100
        attendance_records.append({
            "name": name,
            "id": person_id,
            "total_days": total_days,
            "present": present,
            "percentage": percentage,
            "status": attendance_status(percentage)
        })
        added += 1
        print("Attendance recorded successfully!")

    if added == 0:
        print("No attendance records were added.")


def attendance_report():
    """Display attendance details and summary statistics."""
    print("\n--- ATTENDANCE REPORT ---")
    if not attendance_records:
        no_records("No attendance records available.")
        return

    print(f"{'Name':<18}{'ID':<12}{'Present':>9}{'Total':>8}"
          f"{'Percent':>11}  {'Status'}")
    print_line()
    for item in attendance_records:
        print(f"{item['name']:<18}{item['id']:<12}{item['present']:>9}"
              f"{item['total_days']:>8}{item['percentage']:>10.2f}%  "
              f"{item['status']}")
    print_line()

    count = len(attendance_records)
    average = sum(x["percentage"] for x in attendance_records) / count
    highest = max(attendance_records, key=lambda x: x["percentage"])
    lowest = min(attendance_records, key=lambda x: x["percentage"])
    statuses = {name: sum(1 for x in attendance_records if x["status"] == name)
                for name in ("Eligible", "Warning", "Shortage")}

    print(f"Total people       : {count}")
    print(f"Average attendance : {average:.2f}%")
    print(f"Highest            : {highest['name']} ({highest['percentage']:.2f}%)")
    print(f"Lowest             : {lowest['name']} ({lowest['percentage']:.2f}%)")
    print("Eligible: {Eligible} | Warning: {Warning} | Shortage: {Shortage}".format(
        **statuses
    ))


def attendance_menu():
    while True:
        print("\n========== ATTENDANCE MANAGEMENT ==========")
        print("1. Add Attendance Records")
        print("2. View Attendance Report")
        print("3. Back to Main Menu")
        choice = get_int("Enter your choice (1-3): ", 1, 3)
        if choice == 1:
            mark_attendance()
        elif choice == 2:
            attendance_report()
        else:
            return
        pause()


# ----------------------------- GRADING MODULE ---------------------------

def calculate_grade(percentage):
    """Return grade and remark according to the required grading scale."""
    if percentage >= 90:
        return "A+", "Outstanding"
    if percentage >= 80:
        return "A", "Excellent"
    if percentage >= 70:
        return "B", "Very Good"
    if percentage >= 60:
        return "C", "Good"
    if percentage >= 50:
        return "D", "Satisfactory"
    if percentage >= 35:
        return "E", "Pass"
    return "F", "Fail"


def add_student_result():
    """Enter marks for one student and store the calculated result."""
    print("\n--- ENTER STUDENT MARKS ---")
    name = get_name("Student name: ")
    while True:
        raw_count = input("Number of subjects (press Enter for default 5): ").strip()
        if raw_count == "":
            subject_count = 5
            break
        try:
            subject_count = int(raw_count)
            if 1 <= subject_count <= 20:
                break
            print("Enter a whole number between 1 and 20.")
        except ValueError:
            print("Invalid input. Please enter a whole number.")
    subjects = []
    marks = []
    for number in range(subject_count):
        subject = DEFAULT_SUBJECTS[number] if number < len(DEFAULT_SUBJECTS) \
            else f"Subject {number + 1}"
        mark = get_float(f"{subject} marks (0-100): ", 0, 100)
        subjects.append(subject)
        marks.append(mark)

    total = sum(marks)
    average = total / subject_count
    percentage = (total / (subject_count * 100)) * 100
    grade, remark = calculate_grade(percentage)
    passed = not any(mark < PASS_MARK for mark in marks)
    result = {
        "name": name,
        "subjects": subjects,
        "marks": marks,
        "total": total,
        "average": average,
        "percentage": percentage,
        "grade": grade,
        "remark": remark,
        "result": "PASS" if passed else "FAIL"
    }
    student_records.append(result)
    display_report_card(result)


def display_report_card(student):
    """Print one student's report card."""
    print("\n" + "=" * 34 + " REPORT CARD " + "=" * 31)
    print(f"Student: {student['name']}")
    print_line()
    print(f"{'Subject':<22}{'Marks':>10}")
    print_line()
    for subject, mark in zip(student["subjects"], student["marks"]):
        print(f"{subject:<22}{mark:>10.2f}")
    print_line()
    print(f"{'Total':<22}{student['total']:>10.2f}")
    print(f"{'Average':<22}{student['average']:>10.2f}")
    print(f"{'Percentage':<22}{student['percentage']:>9.2f}%")
    print(f"{'Grade':<22}{student['grade']:>10}")
    print(f"{'Remark':<22}{student['remark']:>10}")
    print(f"{'Final Result':<22}{student['result']:>10}")
    if student["result"] == "FAIL":
        print("A student fails if any one subject mark is below 35.")
    print("=" * 78)


def class_summary():
    """Show class average, topper, pass count and fail count."""
    print("\n--- CLASS SUMMARY ---")
    if not student_records:
        no_records("No student records available.")
        return
    count = len(student_records)
    class_average = sum(s["percentage"] for s in student_records) / count
    topper = max(student_records, key=lambda s: s["percentage"])
    pass_count = sum(1 for s in student_records if s["result"] == "PASS")
    fail_count = count - pass_count
    print(f"Total students : {count}")
    print(f"Class average  : {class_average:.2f}%")
    print(f"Topper         : {topper['name']} ({topper['percentage']:.2f}%)")
    print(f"Pass count     : {pass_count}")
    print(f"Fail count     : {fail_count}")


def grading_menu():
    while True:
        print("\n========== GRADING SYSTEM ==========")
        print("1. Enter Student Marks")
        print("2. View All Report Cards")
        print("3. Class Summary")
        print("4. Back to Main Menu")
        choice = get_int("Enter your choice (1-4): ", 1, 4)
        if choice == 1:
            add_student_result()
        elif choice == 2:
            if not student_records:
                no_records("No student records available.")
            else:
                for student in student_records:
                    display_report_card(student)
        elif choice == 3:
            class_summary()
        else:
            return
        pause()


# ------------------------------ BILLING MODULE --------------------------

def calculate_discount(subtotal):
    """Return the discount rate for the applicable subtotal slab."""
    if subtotal >= Decimal("10000"):
        return Decimal("0.15")
    if subtotal >= Decimal("5000"):
        return Decimal("0.10")
    if subtotal >= Decimal("1000"):
        return Decimal("0.05")
    return Decimal("0.00")


def calculate_tax(taxable_amount, tax_rate=TAX_RATE):
    """Calculate tax on the amount remaining after discount."""
    return money(taxable_amount * tax_rate)


def generate_invoice():
    """Create an invoice with multiple items, discount and tax."""
    print("\n--- CREATE CUSTOMER BILL ---")
    customer = get_name("Customer name: ")
    bill_number = f"INV-{len(invoices) + 1:04d}"
    items = []

    print("Enter bill items. Type 'done' when all items have been entered.")
    while True:
        item_name = input("Item name (or done): ").strip()
        if item_name.casefold() == "done":
            break
        if not 1 <= len(item_name) <= 40:
            print("Item name must contain 1-40 characters.")
            continue
        price = get_money("Unit price: ")
        quantity = get_int("Quantity: ", 1)
        line_total = money(price * quantity)
        items.append({
            "name": item_name,
            "price": price,
            "quantity": quantity,
            "total": line_total
        })
        print(f"Item added. Line total: {line_total:.2f}")

    if not items:
        print("No items added. Invoice was not created.")
        return

    subtotal = money(sum((item["total"] for item in items), Decimal("0.00")))
    discount_rate = calculate_discount(subtotal)
    discount_amount = money(subtotal * discount_rate)
    taxable_amount = money(subtotal - discount_amount)
    tax_amount = calculate_tax(taxable_amount)
    grand_total = money(taxable_amount + tax_amount)

    invoice = {
        "bill_number": bill_number,
        "date": date.today().isoformat(),
        "customer": customer,
        "items": items,
        "subtotal": subtotal,
        "discount_rate": discount_rate,
        "discount_amount": discount_amount,
        "taxable_amount": taxable_amount,
        "tax_amount": tax_amount,
        "grand_total": grand_total
    }
    invoices.append(invoice)
    display_invoice(invoice)


def display_invoice(invoice):
    """Print a formatted invoice."""
    print("\n" + "=" * 29 + " INVOICE " + "=" * 40)
    print(f"Bill No.: {invoice['bill_number']}       Date: {invoice['date']}")
    print(f"Customer: {invoice['customer']}")
    print_line()
    print(f"{'Item':<24}{'Price':>12}{'Qty':>8}{'Total':>14}")
    print_line()
    for item in invoice["items"]:
        print(f"{item['name']:<24}{item['price']:>12.2f}"
              f"{item['quantity']:>8}{item['total']:>14.2f}")
    print_line()
    print(f"{'Subtotal':<48}{invoice['subtotal']:>14.2f}")
    rate_percent = invoice["discount_rate"] * 100
    print(f"{f'Discount ({rate_percent:.0f}%)':<48}"
          f"-{invoice['discount_amount']:>13.2f}")
    print(f"{'Taxable amount':<48}{invoice['taxable_amount']:>14.2f}")
    print(f"{'Tax (18%)':<48}{invoice['tax_amount']:>14.2f}")
    print_line("=")
    print(f"{'GRAND TOTAL':<48}{invoice['grand_total']:>14.2f}")
    print("\nThank you for your purchase!")


def billing_menu():
    while True:
        print("\n========== BILLING SYSTEM ==========")
        print("1. Create Customer Bill")
        print("2. View All Invoices")
        print("3. Back to Main Menu")
        choice = get_int("Enter your choice (1-3): ", 1, 3)
        if choice == 1:
            generate_invoice()
        elif choice == 2:
            if not invoices:
                no_records("No invoices available.")
            else:
                for invoice in invoices:
                    display_invoice(invoice)
        else:
            return
        pause()


# ------------------------------- REPORTS MODULE -------------------------

def view_reports():
    """Open the report menu and show the report selected by the user."""
    while True:
        print("\n========== VIEW REPORTS ==========")
        print("1. Expense Report")
        print("2. Attendance Report")
        print("3. Grading Report")
        print("4. Billing Report")
        print("5. Back to Main Menu")
        choice = get_int("Enter your choice (1-5): ", 1, 5)
        if choice == 1:
            view_expenses()
            expense_summary()
        elif choice == 2:
            attendance_report()
        elif choice == 3:
            if not student_records:
                no_records("No student records available.")
            else:
                class_summary()
                for student in student_records:
                    display_report_card(student)
        elif choice == 4:
            if not invoices:
                no_records("No invoices available.")
            else:
                for invoice in invoices:
                    display_invoice(invoice)
        else:
            return
        pause()


# ------------------------------- MAIN MENU ------------------------------

def display_menu():
    """Display the numbered main menu."""
    print("\n" + "=" * 78)
    print(" EXPENSE, ATTENDANCE, GRADING AND BILLING MANAGEMENT SYSTEM ".center(78))
    print("=" * 78)
    print("1. Expense Management")
    print("2. Attendance Management")
    print("3. Grading System")
    print("4. Billing System")
    print("5. View Reports")
    print("6. Exit")
    print_line()


def main():
    """Run the application until the user chooses Exit."""
    print("Welcome to the Management System!")
    try:
        while True:
            display_menu()
            choice = get_int("Enter your choice (1-6): ", 1, 6)
            if choice == 1:
                expense_menu()
            elif choice == 2:
                attendance_menu()
            elif choice == 3:
                grading_menu()
            elif choice == 4:
                billing_menu()
            elif choice == 5:
                view_reports()
            elif choice == 6:
                print("Thank you for using the system. Goodbye!")
                break
    except (KeyboardInterrupt, EOFError):
        print("\nProgram stopped safely. Goodbye!")
    finally:
        print("Session ended.")


if __name__ == "__main__":
    main()
