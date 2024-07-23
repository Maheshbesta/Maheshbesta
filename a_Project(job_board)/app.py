from flask import *
import mysql.connector
from mysql.connector import errorcode
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your own secret key

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file size to 16MB

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='95506@Mahi',
        database='job_board'
    )
    cursor = conn.cursor()
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)

# Login        

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        try:
            qry = "SELECT * FROM user WHERE email = %s AND password = %s"
            cursor.execute(qry, (email, password))
            account = cursor.fetchone()
            print("IN LOGIN: ", account)
            if account:
                session['loggedin'] = True
                session['user_id'] = account[0]  # Assuming the first column is the ID
                session['email'] = account[3]
                session['role'] = account[4]
                msg = 'Logged in successfully!'
                if session['role'] == 'Employer':
                    # return render_template('emp_dashboard.html', msg=msg,)
                    return redirect(url_for('emp_dashboard'))
                elif session['role'] == 'Job seeker':
                    # return render_template('seeker_dashboard.html', msg=msg)
                    return redirect(url_for('seeker_dashboard'))
                else:
                    msg = 'Unknown role!'
            else:
                msg = 'Incorrect username/password!'
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
            msg = 'An error occurred. Please try again later.'
    return render_template('login.html', msg=msg)

@app.route('/seeker_dashboard')
def seeker_dashboard():
    cursor = conn.cursor()

    # Get search and pagination parameters
    title = request.args.get('title')
    location = request.args.get('location')
    industry = request.args.get('industry')
    job_type = request.args.get('type')
    page = int(request.args.get('page', 1))
    per_page = 3

    # Build the query with search filters
    query = "SELECT * FROM job WHERE 1=1"
    params = []

    if title:
        query += " AND title LIKE %s"
        params.append(f"%{title}%")
    if location:
        query += " AND location LIKE %s"
        params.append(f"%{location}%")
    if industry:
        query += " AND industry LIKE %s"
        params.append(f"%{industry}%")
    if job_type:
        query += " AND type = %s"
        params.append(job_type)

    # Add pagination to the query
    query += " LIMIT %s OFFSET %s"
    params.extend([per_page, (page - 1) * per_page])

    cursor.execute(query, params)
    jobs = cursor.fetchall()

    # Count total jobs for pagination
    count_query = "SELECT COUNT(*) FROM job WHERE 1=1"
    count_params = []

    if title:
        count_query += " AND title LIKE %s"
        count_params.append(f"%{title}%")
    if location:
        count_query += " AND location LIKE %s"
        count_params.append(f"%{location}%")
    if industry:
        count_query += " AND industry LIKE %s"
        count_params.append(f"%{industry}%")
    if job_type:
        count_query += " AND type = %s"
        count_params.append(job_type)

    cursor.execute(count_query, count_params)
    total_jobs = cursor.fetchone()[0]
    total_pages = (total_jobs + per_page - 1) // per_page

    return render_template('seeker_dashboard.html', jobs=jobs, page=page, total_pages=total_pages, msg="Search results")

# @app.route('/seeker_dashboard')
# def seeker_dashboard():
    
#     cursor = conn.cursor()

#     title = request.args.get('title')
#     location = request.args.get('location')
#     industry = request.args.get('industry')
#     job_type = request.args.get('type')

#     query = "SELECT * FROM job WHERE 1=1"
#     params = []

#     if title:
#         query += " AND title LIKE %s"
#         params.append(f"%{title}%")
#     if location:
#         query += " AND location LIKE %s"
#         params.append(f"%{location}%")
#     if industry:
#         query += " AND industry LIKE %s"
#         params.append(f"%{industry}%")
#     if job_type:
#         query += " AND type = %s"
#         params.append(job_type)

#     cursor.execute(query, params)
#     jobs = cursor.fetchall()
    

#     return render_template('seeker_dashboard.html', jobs=jobs, msg="Search results")


@app.route('/forgot')
def forgot():
    return render_template('forgot_password.html')



# ForgotPassword

@app.route('/forgot_password', methods=['POST','GET'])
def forgot_password():
    msg = ''
    if request.method == 'POST' and 'email' in request.form:
        email = request.form['email']
        print("Email address")
        cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
        account = cursor.fetchone()
        
        
        if account:
            msg = 'Account exists!'
            return redirect(url_for('recover_password'),account=account)
        else:
            msg='Acount does not exist'
            return redirect('login.htnl', msg=msg)
           
# # Recover password
# @app.route('/recover/<mail>', methods=['GET', 'POST'])
# def recover(mail):
#     msg = ''
#     if request.method == 'POST' and 'email' in request.form:
#         email = request.form['email']
#         try:
#             cursor.execute('SELECT * FROM user WHERE email = %s', (mail,))
#             account = cursor.fetchone()
#             if account:
#                 msg = 'Account exists!'
               
#             if not email:
#                 msg = 'Please fill out the form!'
            
#         except mysql.connector.Error as e:
#             print("Error executing SQL query:", e)
#             msg = 'An error occurred. Please try again later.'
#     elif request.method == 'POST':
#         msg = 'Please fill out the form!'
#     return render_template('recover_password.html', msg=msg)        


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form and 'role' in request.form:
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        role = request.form['role']
        try:
            cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
            account = cursor.fetchone()
            if account:
                msg = 'Account already exists!'
            elif not name or not password or not email or not role:
                msg = 'Please fill out the form!'
            else:
                
                cursor.execute('INSERT INTO user (name, password, email, role) VALUES (%s, %s, %s, %s)', (name, password, email, role))
                conn.commit()
                msg = 'You have successfully registered!'
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
            msg = 'An error occurred. Please try again later.'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)



@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('name', None)
    return redirect(url_for('login'))

@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    if 'loggedin' in session:
        user_id = session['user_id']
        if request.method == 'POST':
            # Get form data
            title = request.form['title']
            desc = request.form['desc']
            req = request.form['req']
            loc = request.form['loc']
            industry= request.form['industry']
            type = request.form['type']
            print(title, desc, industry, type)
            try:
                cursor.execute(
                    "INSERT INTO job (emp_id,title, description, requirements, location,industry,type) VALUES (%s,%s, %s, %s, %s,%s,%s)",
                    (user_id,title,desc,req, loc,industry,type)
                )
                conn.commit()
                print(title, desc, industry, type)
                flash('Course added successfully!')
                return redirect(url_for('emp_dashboard'))
                # return redirect(url_for('emp_dashboard'))
            except mysql.connector.Error as e:
                print("Error executing SQL query:", e)
                flash('An error occurred. Please try again later.')
            return redirect(url_for('emp_dashboard'))
            
        else:
            return render_template('add_post.html') 
    return render_template('login.html')           



@app.route('/emp_dashboard', methods=['GET'])
def emp_dashboard():
    if 'loggedin' in session:
        emp_id = session['user_id']
        per_page = 3  # Number of jobs per page
        page = request.args.get('page', 1, type=int)  # Current page number

        try:
            cursor.execute("SELECT COUNT(*) FROM job WHERE emp_id = %s", (emp_id,))
            total_jobs = cursor.fetchone()[0]  # Total number of jobs for the employer

            cursor.execute("SELECT * FROM job WHERE emp_id = %s LIMIT %s OFFSET %s",
                           (emp_id, per_page, (page - 1) * per_page))
            jobs = cursor.fetchall()

            total_pages = (total_jobs + per_page - 1) // per_page  # Total number of pages
            return render_template('emp_dashboard.html', jobs=jobs, page=page, total_pages=total_pages)
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


# @app.route('/emp_dashboard')
# def emp_dashboard():
#     id = session['user_id']
#     if 'loggedin' in session:
#             # cursor=conn.cursor()
#             cursor.execute("SELECT * FROM job where emp_id= %s",(id,))
#             print("Data Fetching Successfully")
#             jobs = cursor.fetchall()
#             print("Data Fetching Successfully")
#             print(jobs)
#             return render_template('emp_dashboard.html', jobs=jobs)
#     else:
#         return redirect(url_for('login'))
    
@app.route('/edit_post/<ID>', methods=['GET', 'POST'])
def edit_post(ID):
    msg = ''
    if 'loggedin' in session:
        
        if request.method == 'POST':
            title = request.form['title']
            desc = request.form['desc']
            req = request.form['req']
            loc = request.form['loc']
            industry = request.form['industry']
            type = request.form['type']
            
            try:
                cursor.execute('UPDATE job SET title = %s, description = %s, requirements = %s, location = %s, industry = %s, type = %s WHERE job_id = %s', 
                               (title, desc, req, loc, industry, type, ID))
                conn.commit()
                msg = 'Post updated successfully!'
                return redirect(url_for('emp_dashboard', msg=msg))
            except mysql.connector.Error as e:
                print("Error executing SQL query:", e)
                msg = 'An error occurred. Please try again later.'
                return redirect(url_for('emp_dashboard', msg=msg))
        
        cursor.execute('SELECT * FROM job WHERE job_id = %s', (ID,))
        row = cursor.fetchone()
        if row:
            return render_template('edit_post.html', row=row)
        else:
            msg = 'Post not found!'
            return redirect(url_for('emp_dashboard', msg=msg))
    return redirect(url_for('login'))    
    
@app.route('/delete/<int:ID>')
def delete(ID):
    msg = ''
    if 'loggedin' in session:
        try:
            cursor.execute('DELETE FROM job WHERE job_id = %s', (ID,))
            conn.commit()
            msg = 'post deleted successfully!'
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
            msg = 'An error occurred. Please try again later.'
        return redirect(url_for('emp_dashboard'))
    return redirect(url_for('login'))



@app.route('/apply', methods=['GET', 'POST'])
def apply():
        return render_template('job_application.html')

@app.route('/application', methods=['GET', 'POST'])
def application():
    if 'loggedin' in session:
        user_id=session['user_id']
        if request.method == 'POST':
            letter = request.form['letter']
            resume = request.files['resume']
            
            if resume:
                filename = secure_filename(resume.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                resume.save(file_path)
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO apply (seeker_id,cover_letter, resume) VALUES (%s,%s, %s)",
                        (user_id,letter, filename)
                    )
                    conn.commit()
                    
                    
                    flash('Applied successfully')
                    return redirect(url_for('seeker_dashboard'))
                except mysql.connector.Error as e:
                    print("Error executing SQL query:", e)
                    flash('An error occurred. Please try again later.')
                    return redirect(url_for('seeker_dashboard'))
                

    # return render_template('application_form.html')
    return render_template('job_application.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/applied')
def applied():
    # id = session['user_id']
    print(id)
    if 'loggedin' in session:
        cursor = conn.cursor(dictionary=True)
        # cursor.execute("SELECT j.job_id AS job_id, a.* FROM job AS j INNER JOIN apply AS a ON j.emp_id = a.seeker_id WHERE j.emp_id != a.seeker_id ")
        cursor.execute("select * from apply")                     
        applications = cursor.fetchall()
        return render_template('applications.html', applications=applications)
    else:
        return redirect(url_for('emp_dashboard'))


@app.route('/reply/<ID>', methods=['GET', 'POST'])
def reply(ID):
    if 'loggedin' in session:
        
        cursor = conn.cursor(buffered=True)
        if request.method == 'POST':
            id=request.form['seeker_id']
            # resume =request.files['resume']
            letter=request.form['letter']
            status = request.form['status']
            try:
                    cursor = conn.cursor(buffered=True)
                    cursor.execute(
                        "INSERT INTO application (seeker_id,cover_letter,status) VALUES (%s, %s,%s)",
                        (id, letter,status)
                    )
                    conn.commit()
                    
                    flash('sent successfully')
                    return redirect(url_for('applied'))
            except mysql.connector.Error as e:
                    print("Error executing SQL query:", e)
                    flash('An error occurred. Please try again later.')
                    return redirect(url_for('emp_dashboard'))

            
        cursor =conn.cursor(buffered=True)
        # cursor.execute("SELECT j.job_id AS job_id, a.* FROM job AS j INNER JOIN apply AS a ON j.emp_id = a.seeker_id WHERE j.emp_id != a.seeker_id ")
        cursor.execute("select j.job_id,a.* from job as j inner join apply as a on j.emp_id != a.seeker_id  where seeker_id =%s",(ID,))                     
        row= cursor.fetchone()
        print(row)
        return render_template('reply.html', row=row)
    else:
        return redirect(url_for('emp_dashboard'))





if __name__ == '__main__':
    app.run(debug=True)
