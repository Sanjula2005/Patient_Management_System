from flask import Flask, render_template, request, redirect, url_for, session, abort
from functools import wraps
from config import get_db_connection
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not session.get('logged_in'):
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                return abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator

@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd  = request.form['password']
        db   = get_db_connection()
        cur  = db.cursor()
        cur.execute("SELECT UserID, Role, LinkedID FROM Users WHERE Username=%s AND Password=%s",
                    (user, pwd))
        row = cur.fetchone()
        db.close()

        if not row:
            return "Invalid credentials!", 401

        session['logged_in'] = True
        session['user_id']   = row[0]
        session['role']      = row[1]
        session['linked_id'] = row[2]

        if row[1] == 'admin':
            return redirect(url_for('dashboard'))
        elif row[1] == 'doctor':
            return redirect(url_for('doctor_dashboard'))
        else:
            return redirect(url_for('patient_dashboard'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ─── Admin Dashboard ───────────────────────────────────────
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required('admin')
def dashboard():
    db = get_db_connection()
    cur = db.cursor()

    # Fetch dropdown data
    cur.execute("SELECT DISTINCT Name FROM Doctors")
    doctor_names = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT DISTINCT Name FROM Patients")
    patient_names = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT DISTINCT Specialization FROM Doctors")
    specializations = [row[0] for row in cur.fetchall()]

    # Search & Sort
    search_text = request.form.get('search', '')
    selected_doc = request.form.get('filter_doctor', '')
    selected_pat = request.form.get('filter_patient', '')
    selected_spec = request.form.get('filter_spec', '')
    sort_option   = request.form.get('sort_by', '')

    # Patients query
    query = "SELECT * FROM Patients WHERE Name LIKE %s"
    params = ['%' + search_text + '%']

    if selected_pat:
        query += " AND Name = %s"
        params.append(selected_pat)

    if sort_option == 'name_asc':
        query += " ORDER BY Name ASC"
    elif sort_option == 'name_desc':
        query += " ORDER BY Name DESC"
    elif sort_option == 'age_asc':
        query += " ORDER BY Age ASC"
    elif sort_option == 'age_desc':
        query += " ORDER BY Age DESC"

    cur.execute(query, params)
    patients = cur.fetchall()

    # Doctors query
    doc_query = "SELECT * FROM Doctors WHERE Name LIKE %s"
    doc_params = ['%' + search_text + '%']

    if selected_doc:
        doc_query += " AND Name = %s"
        doc_params.append(selected_doc)
    if selected_spec:
        doc_query += " AND Specialization = %s"
        doc_params.append(selected_spec)

    cur.execute(doc_query, doc_params)
    doctors = cur.fetchall()

    db.close()
    return render_template('dashboard.html',
                           patients=patients,
                           doctors=doctors,
                           doctor_names=doctor_names,
                           patient_names=patient_names,
                           specializations=specializations,
                           search=search_text,
                           selected_doc=selected_doc,
                           selected_pat=selected_pat,
                           selected_spec=selected_spec,
                           sort_option=sort_option)


@app.route('/query', methods=['GET','POST'])
@login_required('admin')
def query():
    db      = get_db_connection()
    cur     = db.cursor()
    cur.execute("SELECT DoctorID, Name FROM Doctors")
    doctors = cur.fetchall()
    cur.execute("SELECT PatientID, Name FROM Patients")
    patients = cur.fetchall()

    reports = []
    headers = []
    if request.method == 'POST' and request.form.get('search_reports'):
        doc_id = request.form.get('doctor_id')
        pat_id = request.form.get('patient_id')
        sql    = """SELECT D.Name AS Doctor, P.Name AS Patient, M.Diagnosis, M.TestType
                    FROM MedicalReports M
                    JOIN Doctors D ON M.DoctorID=D.DoctorID
                    JOIN Patients P ON M.PatientID=P.PatientID
                    WHERE 1=1"""
        params = []
        if doc_id:
            sql += " AND M.DoctorID=%s"; params.append(doc_id)
        if pat_id:
            sql += " AND M.PatientID=%s"; params.append(pat_id)
        cur.execute(sql, tuple(params))
        reports = cur.fetchall()

    custom_results = []
    if request.method == 'POST' and request.form.get('custom_sql'):
        try:
            cur.execute(request.form['custom_sql'])
            custom_results = cur.fetchall()
            headers = [d[0] for d in cur.description]
        except Exception as e:
            custom_results = [('Error: '+str(e),)]

    db.close()
    return render_template('query.html',
                           doctors=doctors,
                           patients=patients,
                           reports=reports,
                           custom_results=custom_results,
                           headers=headers)

@app.route('/add_doctor', methods=['GET','POST'])
@login_required('admin')
def add_doctor():
    if request.method == 'POST':
        nm  = request.form['name']
        spec= request.form['specialization']
        cont= request.form['contact']
        usr = request.form['username']
        pwd = request.form['password']

        db  = get_db_connection()
        cur = db.cursor()
        cur.execute("INSERT INTO Doctors (Name, Specialization, Contact) VALUES (%s,%s,%s)",
                    (nm, spec, cont))
        doc_id = cur.lastrowid
        cur.execute("INSERT INTO Users (Username, Password, Role, LinkedID) VALUES (%s,%s,'doctor',%s)",
                    (usr, pwd, doc_id))
        db.commit()
        db.close()
        return redirect(url_for('dashboard'))
    return render_template('add_doctor.html')

@app.route('/add_patient', methods=['GET', 'POST'])
@login_required()
def add_patient():
    role = session.get('role')
    linked_id = session.get('linked_id')

    db = get_db_connection()
    cur = db.cursor()

    # Only admins see all doctors
    if role == 'admin':
        cur.execute("SELECT DoctorID, Name FROM Doctors")
        doctors = cur.fetchall()
    else:
        # For doctors, fetch their own name
        cur.execute("SELECT DoctorID, Name FROM Doctors WHERE DoctorID = %s", (linked_id,))
        doctors = cur.fetchall()

    if request.method == 'POST':
        name     = request.form['name']
        age      = request.form['age']
        gender   = request.form['gender']
        contact  = request.form['contact']
        address  = request.form['address']
        doctor_id = linked_id if role == 'doctor' else request.form['doctor_id']
        diagnosis = request.form['diagnosis']
        test_type = request.form['test_type']
        username  = request.form['username']
        password  = request.form['password']
        report_date = datetime.date.today()

        cur.execute("INSERT INTO Patients (Name, Age, Gender, Contact, Address) VALUES (%s, %s, %s, %s, %s)",
                    (name, age, gender, contact, address))
        patient_id = cur.lastrowid

        cur.execute("""INSERT INTO MedicalReports (PatientID, DoctorID, ReportDate, Diagnosis, TestType)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (patient_id, doctor_id, report_date, diagnosis, test_type))

        cur.execute("INSERT INTO Users (Username, Password, Role, LinkedID) VALUES (%s, %s, 'patient', %s)",
                    (username, password, patient_id))

        db.commit()
        db.close()

        return redirect(url_for('dashboard') if role == 'admin' else url_for('doctor_dashboard'))

    db.close()
    return render_template('add_patient.html', doctors=doctors, role=role)


@app.route('/doctor_dashboard', methods=['GET','POST'])
@login_required('doctor')
def doctor_dashboard():
    doc_id = session['linked_id']
    search = request.form.get('search','')
    db  = get_db_connection()
    cur = db.cursor()
    cur.execute("""
      SELECT P.* FROM Patients P
      JOIN MedicalReports M ON P.PatientID=M.PatientID
      WHERE M.DoctorID=%s AND P.Name LIKE %s
    """, (doc_id, '%'+search+'%'))
    patients = cur.fetchall()
    db.close()
    return render_template('doctor_dashboard.html', patients=patients, search=search)

@app.route('/patient_dashboard')
@login_required('patient')
def patient_dashboard():
    pat_id = session['linked_id']
    db  = get_db_connection()
    cur = db.cursor()
    cur.execute("""SELECT P.Name,P.Age,P.Gender,P.Contact,P.Address,
                         M.Diagnosis,M.TestType,M.ReportDate,D.Name
                   FROM Patients P
                   JOIN MedicalReports M ON P.PatientID=M.PatientID
                   JOIN Doctors D ON M.DoctorID=D.DoctorID
                   WHERE P.PatientID=%s""", (pat_id,))
    info = cur.fetchone()
    db.close()
    return render_template('patient_dashboard.html', info=info)

if __name__ == '__main__':
    app.run(debug=True)
