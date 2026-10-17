import matplotlib.pyplot as plt # imports matplotlib to create graphs
import pandas as pd # imports pandas to create dataframes and perform calculations


MONTH_ORDER = { # stores the calendar number for each month so months can be sorted correctly
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12
}

expenses = {} # creates a dictionary to store expenses using key-value pairs

year = int(input("Enter Year: ")) # takes the year as an integer
month = input("Enter Month: ").capitalize() # takes the month as text and capitalizes its first letter
date = int(input("Enter Date: ")) # takes the date as an integer
print() # prints an empty line
item = input("Enter Expense Category: ").lower() # takes the category as lowercase text
amount = int(input(f"Enter {item} Amount: ")) # takes the expense amount as an integer


def add_expenses(year, month, date, item, amount): # adds one expense to the nested expenses dictionary
    # The parameters tell the function where to store the expense and what data to store.
    expenses.setdefault(year, {}) 
    expenses[year].setdefault(month, {})
    expenses[year][month].setdefault(date, []) 

    expenses[year][month][date].append({
        "Expense Category": item,
        "Amount": amount
    })

    # Each date contains a list because more than one expense can happen on the same date.
    # Each expense in that list is a dictionary containing its category and amount.
    # setdefault creates a key only when it does not already exist, so existing data is not overwritten.
    print()


def create_dataframe(expenses): # changes the nested expense data into a sorted pandas table
    # A DataFrame is a table with named columns, similar to a spreadsheet.
    rows = [] # creates an empty list where each expense will become one row

    for year, months in expenses.items(): 
        for month, dates in months.items():
            for date, expense_list in dates.items():
                for expense in expense_list:
                    rows.append({
                        "Year": year,
                        "Month": month,
                        "Date": date,
                        "Category": expense["Expense Category"],
                        "Amount": expense["Amount"]
                    })

    # The loops move through each level of the nested dictionary: year, month, date, and expense.
    # Each expense is flattened into one dictionary and added as one row in the rows list.

    df = pd.DataFrame(rows) # uses pandas to turn the rows list into a dataframe
    df["Month Number"] = df["Month"].map(MONTH_ORDER) # maps each month name to its calendar number

    return df.sort_values(
        by=["Year", "Month Number", "Date"] # sorts by year, calendar month number, and date
    )


def display_expenses(expenses):
    # This function prints every expense grouped by year, month, and date.
    df = create_dataframe(expenses) # creates one sorted dataframe to use for displaying

    for year in df["Year"].unique(): # unique gives every year only once
        print(f"===== Year -> {year} =====")

        year_df = df[df["Year"] == year] # creates a dataframe containing only the current year

        for month in year_df["Month"].unique(): # gets each month inside the current year
            print(f"----- Month -> {month} -----")

            month_df = year_df[year_df["Month"] == month] # filters the current year to the current month

            for date in month_df["Date"].unique(): # gets each date inside the current month
                print(f"***** Date -> {date} *****")

                date_df = month_df[month_df["Date"] == date] # filters the current month to the current date

                print()
                print(
                    date_df[["Category", "Amount"]]
                    .to_string(index=False)
                )
                print()


def save_to_csv(expenses):
    # This function saves the expense table as expenses.csv.
    df = create_dataframe(expenses)
    df = df.drop(columns=["Month Number"]) # removes the helper column before saving
    df = df.rename(columns={"Category": "Expense Category"}) # changes the column name for the CSV

    df.to_csv("expenses.csv", index=False) # saves the dataframe as a CSV file without row numbers


def display_financial_summary(expenses):
    # This function prints totals, averages, and biggest categories for each year and month.
    df = create_dataframe(expenses) # uses the same sorted dataframe for the summary

    for year in df["Year"].unique():
        print(f"===== Year -> {year} =====")

        year_df = df[df["Year"] == year]
        total_year = year_df["Amount"].sum() # adds all expenses in the current year

        category_totals_year = year_df.groupby("Category")["Amount"].sum() # adds spending for each category
        biggest_category_year = category_totals_year.idxmax() # finds the category with the highest total
        biggest_amount_year = category_totals_year.max() # finds the highest category total

        print(f"Total = {total_year}")
        print(f"Average = {total_year / 12:.2f}")
        print(
            f"Most expensive category = "
            f"{biggest_category_year} : ({biggest_amount_year})"
        )

        for month in year_df["Month"].unique():
            print(f"----- Month -> {month} -----")

            month_df = year_df[year_df["Month"] == month]
            total_month = month_df["Amount"].sum() # adds all expenses in the current month

            category_totals_month = (
                month_df.groupby("Category")["Amount"].sum()
            ) # adds spending for each category in the current month
            biggest_category_month = category_totals_month.idxmax() # finds the biggest monthly category
            biggest_amount_month = category_totals_month.max() # finds its total amount

            print(f"Total = {total_month}")
            print(f"Average = {month_df['Amount'].mean():.2f}") # mean calculates the average per expense
            print(
                f"Most expensive category = "
                f"{biggest_category_month} ({biggest_amount_month})"
            )


def save_expense_graph(expenses):
    # This function creates and saves either a yearly or monthly line graph.
    df = create_dataframe(expenses) # creates the sorted data used for the graph

    graph_choice = input("""
Graph type:

1. Year-wise expenses
2. Month-wise expenses for a year

Choice: """)

    if graph_choice == "1": # creates totals grouped by year
        totals = df.groupby("Year")["Amount"].sum().sort_index() # calculates total spending for each year
        x_values = totals.index # x-axis values are the years
        y_values = totals.values # y-axis values are the yearly totals
        file_name = "yearly_expenses.png"
        title = "Total Expenses by Year"
        x_label = "Year"

    elif graph_choice == "2": # creates totals grouped by month for one selected year
        selected_year = int(input("Enter Year: "))
        year_df = df[df["Year"] == selected_year] # keeps only expenses from the selected year

        if year_df.empty:
            print(f"No expenses found for {selected_year}.") # stops if the selected year has no data
            return

        totals = (
            year_df.groupby("Month Number")["Amount"]
            .sum()
            .sort_index()
        ) # calculates monthly totals and keeps them in calendar order

        x_values = [
            list(MONTH_ORDER)[month_number - 1]
            for month_number in totals.index
        ] # changes month numbers back into month names for the graph
        y_values = totals.values
        file_name = f"monthly_expenses_{selected_year}.png"
        title = f"Monthly Expenses for {selected_year}"
        x_label = "Month"

    else:
        print("Invalid graph choice.")
        return

    plt.figure(figsize=(10, 6)) # creates the graph area
    plt.plot(x_values, y_values, linestyle="-") # draws a line using the x and y values
    plt.title(title) # adds a title to the graph
    plt.xlabel(x_label) # labels the horizontal axis
    plt.ylabel("Total Expenses") # labels the vertical axis

    if graph_choice == "1":
        plt.xticks(x_values) # shows only the actual years instead of decimal intermediate values

    plt.grid(True) # adds grid lines to make values easier to read
    plt.tight_layout() # adjusts spacing so labels fit properly
    plt.savefig(file_name) # saves the graph as an image instead of displaying it
    plt.close() # closes the graph from memory after saving

    print(f"Graph saved as {file_name}")


def add_new_expense():
    # This function asks how the new expense date should relate to the current date.
    # It then collects the expense details and sends them to add_expenses().
    global year, month, date # allows this function to update the current date values

    expense_action = int(input("""
        Add New Expense:

        1. Same date
        2. New date, Same Month
        3. New month, Same Year
        4. New year

        Choice: """))

    if expense_action == 2: # changes only the date
        date = int(input("Enter Date: "))

    elif expense_action == 3: # changes the month and date
        month = input("Enter Month: ").capitalize()
        date = int(input("Enter Date: "))

    elif expense_action == 4: # changes the year, month, and date
        year = int(input("Enter Year: "))
        month = input("Enter Month: ").capitalize()
        date = int(input("Enter Date: "))

    print()
    print(f"Current date -> {date}-{month},{year}")

    item = input("Enter Expense Category: ").lower()
    amount = int(input(f"Enter {item} Amount: "))

    add_expenses(year, month, date, item, amount) # stores the new expense


add_expenses(year, month, date, item, amount) # stores the first expense before showing the menu

while True: # keeps showing the menu until the user chooses exit
    run_input = int(input("""
Next action:

1. Add New Expense
2. Display Expenses
3. Save to CSV
4. Display Financial Summary
5. Save Expense Graph
6. Exit

Choice: """))

    if run_input == 1: # opens the nested menu for adding an expense
        add_new_expense()

    elif run_input == 2: # displays all stored expenses
        display_expenses(expenses)

    elif run_input == 3: # saves all expenses to CSV
        save_to_csv(expenses)

    elif run_input == 4: # displays yearly and monthly financial summaries
        display_financial_summary(expenses)

    elif run_input == 5: # creates and saves a graph
        save_expense_graph(expenses)

    elif run_input == 6: # stops the program
        print("Thanks for Using this, Visit Again!!!")
        break
