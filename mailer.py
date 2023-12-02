import mysql.connector
import smtplib

def connect_database():
    # connecting to the MySQL database
    conn = mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        password = '',
        database = 'maintenance'
    )

    # checking if the connection is successful
    if conn.is_connected():
        print('Connected to MySQL database')
    return conn

############################ STATUS UPDATE #################################################
def update_status(conn):
    cursor = conn.cursor()
    update_query = """
    UPDATE maintenance_machines 
    SET status = CASE
        WHEN CURDATE() < due_from_date THEN 'NOT_DUE'
        WHEN CURDATE() > due_till_date THEN 'OVERDUE'
        ELSE 'PENDING'
    END
    """
    cursor.execute(update_query)
    conn.commit()
    print('Status updated successfully')

conn = connect_database()
update_status(conn)

########################### SEND EMAIL #################################################
def retrieve_email_recipients():
    # querying the database for email recipients
    cursor = conn.cursor()
    query = "SELECT email FROM mail_recipients"
    print(f"Executing query: {query}")
    cursor.execute(query)
    print("Query executed.")

    # fetching all the email recipients
    recipients = [row[0] for row in cursor.fetchall()]

    return recipients

def retrieve_required_rows():
    # querying the database for rows where IS_DONE is set to false
    cursor = conn.cursor()
    query = "SELECT * FROM maintenance_machines WHERE CURDATE() >= DATE_SUB(due_from_date, INTERVAL 1 DAY)"
    print(f"Executing query: {query}")
    cursor.execute(query)
    print("Query executed.")

    # fetching all the matching rows
    rows = cursor.fetchall()
    cursor.close()

    return rows

def construct_email(receiver_email, receiver_name, machines):
    smtp_server = 'smtp.gmail.com'
    port = 587 # for starttls
    
    #enter correct email credentials
    sender_email = 'xyz@gmail.com' 
    sender_password = 'pscg jkva h90q poia'

    subject = 'Maintenance Reminder'
    body = f"<html><body><p>Dear {receiver_name},</p><p>This is a reminder about preventive maintenance of the following equipment:</p>"
    body += "<table border='1'><tr><th>Equipment</th><th>Area</th><th>Due</th></tr>"
    
    for machine in machines:
        item = machine[7]
        # code = machine[5]
        area = machine[6]
        # status = machine[11]
        dueFrom = machine[2]
        dueTill = machine[3]
        body += f"<tr><td>{item}</td><td>{area}</td><td>{dueFrom} to {dueTill}</td></tr>"
    
    body += "</table></body></html>"
    email = f"Subject: {subject}\n"
    email += f"From: {sender_email}\n"
    email += f"To: {receiver_email}\n"
    email += "MIME-Version: 1.0\n"
    email += "Content-Type: text/html\n\n"
    email += body

    # Sending the email
    server = smtplib.SMTP(smtp_server, port)
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, email)
    server.quit()

    # Printing confirmation message
    print(f"Email reminder sent to {receiver_email}")


def send_reminders():
    rows = retrieve_required_rows()
    recipients = retrieve_email_recipients()
    machines = []
    
    for row in rows:
        machines.append(row)
    
    for receiver_email in recipients:
        try:
            construct_email(receiver_email, 'Sir/Mam', machines)
        except Exception as e:
            print(f"An error occurred: {e}")

send_reminders()

###################################################################################

# closing the database connection
conn.close()
