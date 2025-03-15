from flask import Flask, render_template, request, jsonify

from chat import get_response

import pyodbc

app = Flask(__name__)


# SQL Server Connection
def get_db_connection():
    return pyodbc.connect('Driver={SQL Server};Server=DESKTOP-M7EQ5UN\SQLEXPRESS;Database=MedAssist;Trusted_Connection=yes;')

# Fetch all data from SQL Server for get bot knowledge
@app.route('/get_table_data', methods=['GET'])
def get_table_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("select Id,TagName, Description from [dbo].[MedAssit]") 
    data = cursor.fetchall()
    
    cursor.close()
    conn.close()

    results = [{"id": row[0], "TagName": row[1], "Description": row[2]} for row in data]
    return jsonify(results)

# Fetch all data from SQL Server for System users
@app.route('/get_table_data_forSystemUser', methods=['GET'])
def get_table_data_for_Systemuser():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("select (FirstName +' '+ LastName) AS Name, Phonenumber,Email, UserName,Password, Role from [dbo].[SystemUsers]")
    data = cursor.fetchall()
    
    cursor.close()
    conn.close()

    results = [{"Name": row[0], "Phonenumber": row[1],"Email": row[2],"UserName": row[3],"Password": row[4],"Role": row[5]} for row in data]
    return jsonify(results)

# Fetch all data from SQL Server for get Asked Questions
@app.route('/get_table_data_Questiones', methods=['GET'])
def get_table_data_Questiones():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("select TagName,Description from [dbo].[MedAssitKnowledge] order by Id desc ") 
    data = cursor.fetchall()
    
    cursor.close()
    conn.close()

    results = [{"TagName": row[0], "Description": row[1]} for row in data]
    return jsonify(results)

# Fetch all data from SQL Server for get User Activity
@app.route('/get_table_data_Activity', methods=['GET'])
def get_table_data_Activity():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("select id,ISNULL(Questions,'') as Questions,AskeDate from [dbo].[MedAssistUnKnownQuestions] order by id desc") 
    data = cursor.fetchall()
    
    cursor.close()
    conn.close()

    results = [{"id": row[0], "Questions": row[1], "AskeDate": row[2]} for row in data]
    return jsonify(results)

# Start Staff Dashboard Data Fetching
#  Data Fetching Patient Details
@app.route('/get_table_data_PatientAppointment', methods=['GET'])
def get_table_data_PatientAppointment():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("select A.AppointmentID as Id, A.AppointmentDate as [Date], CONVERT(VARCHAR(5), A.AppointmentTime, 108) AS [Time], P.UserName As PatientName, (D.FistName+''+D.LastName) As DoctorName,A.AppointmentVanues as	Vanues  from [dbo].[Appointment] A INNER JOIN [dbo].[Doctors] D ON D.DoctorID = A.DoctorID INNER JOIN [dbo].[Patients] P ON P.PatientID = A.PatientID") 
    data = cursor.fetchall()
    
    cursor.close()
    conn.close()

    results = [{"Id": row[0], "Date": row[1], "Time": row[2], "PatientName": row[3],"DoctorName": row[4],"Vanues": row[5]} for row in data]
    return jsonify(results)


# Form Submiting 
@app.route('/submit', methods=['POST'])
def submit():
    try:
        question = request.form.get('question')
        answer = request.form.get('answer')

        if not question:
            return jsonify({'status': 'error', 'message': 'Question cannot be empty!'})

        # Connect to SQL Server
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert data into database
        query = "INSERT INTO [dbo].[MedAssitKnowledge] (TagName, Description) VALUES (?, ?)"       
   
        cursor.execute(query, (question, answer if answer else None))
        conn.commit()

        return jsonify({'status': 'success', 'message': 'Data inserted successfully!'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.get("/")
def index_get():
   return render_template("index.html")

@app.route("/login")
def login():
    return render_template("Login.html")

@app.route("/staff_dashboard")
def staff_dashboard():
    return render_template("StaffDashbord.html")

@app.route("/admin_dashboard")
def admin_dashboard():
    return render_template("AdminDashboard.html")

@app.route("/index")
def index():
    return render_template("index.html")

@app.post("/predict")
def predict():
    text = request.get_json().get("message")
    response = get_response(text)
    message = {"answer": response}
    return jsonify(message)

if __name__ == "__main__":
    app.run(debug=True)  
 
