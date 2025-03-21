import csv
import sqlite3
import os

# Global database connection
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()


def return_cursor():
    """Returns the database cursor (Required for test cases)."""
    return cursor


def main():
    """Main function to initialize database and process data."""
    create_tables()

    # Define the resources directory
    base_dir = os.path.abspath(os.path.join(os.path.dirname(_file_), "../../resources"))

    # Define file paths
    users_csv = os.path.join(base_dir, "users.csv")
    call_logs_csv = os.path.join(base_dir, "callLogs.csv")
    analytics_csv = os.path.join(base_dir, "userAnalytics.csv")
    ordered_calls_csv = os.path.join(base_dir, "orderedCalls.csv")

    # Load and process data
    try:
        load_and_clean_users(users_csv)
        load_and_clean_call_logs(call_logs_csv)
        write_user_analytics(analytics_csv)
        write_ordered_calls(ordered_calls_csv)

        # Uncomment to debug data:
        # select_from_users_and_call_logs()

    except FileNotFoundError as e:
        print(f"Error: {e}")

    # Close the connection
    cursor.close()
    conn.close()


def create_tables():
    """Creates tables and ensures they start empty for testing consistency."""
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS callLogs")

    cursor.execute('''CREATE TABLE users (
                        userId INTEGER PRIMARY KEY AUTOINCREMENT,
                        firstName TEXT NOT NULL,
                        lastName TEXT NOT NULL
                      )''')

    cursor.execute('''CREATE TABLE callLogs (
                        callId INTEGER PRIMARY KEY AUTOINCREMENT,
                        phoneNumber TEXT,
                        startTime INTEGER,
                        endTime INTEGER,
                        direction TEXT,
                        userId INTEGER,
                        FOREIGN KEY (userId) REFERENCES users(userId)
                    )''')
    conn.commit()

def load_and_clean_users(file_path):
    """Loads users from CSV into users table, discarding incomplete records."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"User CSV file not found: {file_path}")

    with open(file_path, 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            print(f"Checking row: {row}")  # Debugging output
            if len(row) == 2 and all(row):  # Ensure exactly 2 fields and no missing values
                cursor.execute("INSERT INTO users (firstName, lastName) VALUES (?, ?)", (row[0].strip(), row[1].strip()))

    conn.commit()

    # Print inserted data
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    print("Users inserted into DB:", users)  # Debugging output



def load_and_clean_call_logs(file_path):
    """Loads call logs from CSV into callLogs table, discarding incomplete records."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Call Logs CSV file not found: {file_path}")

    with open(file_path, 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            if len(row) == 5 and all(row):  # Ensure correct number of fields and no missing values
                cursor.execute("INSERT INTO callLogs (phoneNumber, startTime, endTime, direction, userId) VALUES (?, ?, ?, ?, ?)",
                               (row[0], int(row[1]), int(row[2]), row[3], int(row[4])))
    conn.commit()


def write_user_analytics(csv_file_path):
    """Generates user analytics (avg call duration, call count) and writes to CSV."""
    cursor.execute('''SELECT userId, 
                             AVG(endTime - startTime) AS avgDuration, 
                             COUNT(callId) AS numCalls 
                      FROM callLogs GROUP BY userId''')

    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["userId", "avgDuration", "numCalls"])  # CSV header
        writer.writerows(cursor.fetchall())  # Write query results to CSV


def write_ordered_calls(csv_file_path):
    """Orders call logs by userId, then startTime, and writes to CSV."""
    cursor.execute('''SELECT * FROM callLogs ORDER BY userId, startTime''')

    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["callId", "phoneNumber", "startTime", "endTime", "direction", "userId"])  # CSV header
        writer.writerows(cursor.fetchall())  # Write query results to CSV


def select_from_users_and_call_logs():
    """Prints users and callLogs data for debugging."""
    print("\nPRINTING DATA FROM USERS\n-------------------------")
    cursor.execute("SELECT * FROM users")
    for row in cursor.fetchall():
        print(row)

    print("\nPRINTING DATA FROM CALLLOGS\n-------------------------")
    cursor.execute("SELECT * FROM callLogs")
    for row in cursor.fetchall():
        print(row)


if __name__ == '__main__':
    main()