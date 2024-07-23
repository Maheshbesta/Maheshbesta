from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import mysql.connector
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure key
app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to establish database connection
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='95506@Mahi',
        database='portfolio_db'
    )

# Route for login
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            qry = "SELECT * FROM admin WHERE username = %s AND password = %s"
            cursor.execute(qry, (username, password))
            account = cursor.fetchone()
            if account:
                session['loggedin'] = True
                session['userid'] = account['admin_id']  # Corrected session key to 'userid'
                session['username'] = account['username']
                msg = 'Logged in successfully!'
                return redirect(url_for('home'))
            else:
                msg = 'Incorrect username/password!'
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
            msg = 'An error occurred. Please try again later.'
        finally:
            cursor.close()
            connection.close()
    return render_template('login.html', msg=msg)

# Route for signup
@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM admin WHERE username = %s", (username,))
            account = cursor.fetchone()
            if account:
                msg = 'Account already exists!'
            else:
                cursor.execute("INSERT INTO admin (username, password) VALUES (%s, %s)", (username, password))
                connection.commit()
                msg = 'You have successfully registered!'
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
            msg = 'An error occurred. Please try again later.'
        finally:
            cursor.close()
            connection.close()
    return render_template('sign_up.html', msg=msg)

# Route for home page
@app.route('/home')
def home():
    if 'loggedin' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM admin WHERE admin_id = %s', (session['userid'],))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return render_template('home.html', user=user)
    return redirect(url_for('login'))

# Route for about page
@app.route('/about')
def about():
    if 'loggedin' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM admin WHERE admin_id = %s', (session['userid'],))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return render_template('about.html', user=user)
    return redirect(url_for('login'))

# Route for project gallery
@app.route('/project_gallery')
def project_gallery():
    if 'loggedin' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM projects')
        projects = cursor.fetchall()
        cursor.execute('SELECT * FROM admin WHERE admin_id = %s', (session['userid'],))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return render_template('project_gallery.html', projects=projects, user=user)
    return redirect(url_for('login'))

# Route for resume
@app.route('/resume')
def resume():
    if 'loggedin' in session:
        user_id = session['userid']
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM experiences WHERE user_id = %s", (user_id,))
            experience = cursor.fetchall()
            
            cursor.execute("SELECT * FROM education WHERE user_id = %s", (user_id,))
            education = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            resume = {
                'experiences': experience,
                'education': education
            }
            
            return render_template('resume.html', user=session['username'], resume=resume)
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
            if connection:
                connection.rollback()
            flash('An error occurred. Please try again later.', 'danger')
    return redirect(url_for('login'))

# Route for contact page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if 'loggedin' in session:
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            message = request.form['message']
            
            # Server-side validation
            if not name or not email or not message:
                flash('Please fill out all fields', 'danger')
                return redirect(url_for('contact'))
            
            connection = get_db_connection()
            cursor = connection.cursor()
            try:
                insert_query = "INSERT INTO contact_messages (name, email, message) VALUES (%s, %s, %s)"
                cursor.execute(insert_query, (name, email, message))
                connection.commit()
                flash('Message sent successfully', 'success')
            except mysql.connector.Error as e:
                print("Error executing SQL query:", e)
                flash('Failed to send message', 'danger')
                connection.rollback()
            finally:
                cursor.close()
                connection.close()
            return redirect(url_for('contact'))
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM admin WHERE admin_id = %s', (session['userid'],))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return render_template('contact.html', user=user)
    return redirect(url_for('login'))

# Route for admin dashboard
@app.route('/admin/admin_dashboard', methods=['GET'])
def admin_dashboard():
    if 'loggedin' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM projects")
        projects = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('admin_dashboard.html', projects=projects)
    return redirect(url_for('login'))

# Route for adding a project
@app.route('/admin/add_project', methods=['GET', 'POST'])
def add_project():
    if 'loggedin' in session:
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            technologies = request.form['technologies']
            project_url = request.form['project_url']
            source_url = request.form['source_url']

            # Check if the post request has the file part
            if 'image' not in request.files:
                flash('No file part', 'danger')
                return redirect(request.url)
            file = request.files['image']
            # If the user does not select a file, the browser submits an empty part without filename
            if file.filename == '':
                flash('No selected file', 'danger')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                if not title or not description or not technologies or not project_url or not source_url:
                    flash('Please fill out all fields', 'danger')
                    return redirect(url_for('add_project'))

                try:
                    connection = get_db_connection()
                    cursor = connection.cursor()

                    insert_query = """
                        INSERT INTO projects (title, description, technologies, image_url, project_url, source_url, user_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (title, description, technologies, image_url, project_url, source_url, session['userid']))
                    connection.commit()
                    flash('Project added successfully', 'success')
                    cursor.close()
                    connection.close()
                except mysql.connector.Error as e:
                    print("Error executing SQL query:", e)
                    flash('Failed to add project', 'danger')
                return redirect(url_for('admin_dashboard'))
        
        return render_template('add_project.html')

    return redirect(url_for('login'))


@app.route('/admin/projects')
def projects():
    if 'loggedin' in session:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM projects WHERE user_id = %s', (session['userid'],))
        projects = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('projects.html', projects=projects)
    return redirect(url_for('login'))



@app.route('/admin_resume_1', methods=['GET', 'POST'])
def admin_resume_1():
    if 'loggedin' in session:
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            user_id = session['userid']

            if request.method == 'POST':
                first_name = request.form.get('first_name', '')
                last_name = request.form.get('last_name', '')
                job_title = request.form.get('job_title', '')
                description = request.form.get('description', '')
                profile_image = request.files.get('profile_image')
                email = request.form.get('email', '')
                phone = request.form.get('phone', '')
                address = request.form.get('address', '')
                summary = request.form.get('summary', '')

                update_query = """
                    UPDATE admin 
                    SET first_name = %s, last_name = %s, job_title = %s, description = %s, email = %s, phone = %s, address = %s, summary = %s 
                    WHERE admin_id = %s
                """
                cursor.execute(update_query, (first_name, last_name, job_title, description, email, phone, address, summary, user_id))
                connection.commit()

                if profile_image and allowed_file(profile_image.filename):
                    filename = secure_filename(profile_image.filename)
                    profile_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                    cursor.execute('UPDATE admin SET profile_image = %s WHERE admin_id = %s', (filename, user_id))
                    connection.commit()

                # Update experience details
                company_name = request.form.getlist('company_name')
                job_title_experience = request.form.getlist('job_title_experience')
                start_date = request.form.getlist('start_date')
                end_date = request.form.getlist('end_date')
                description_experience = request.form.getlist('description_experience')

                for i in range(len(company_name)):
                    if company_name[i] and job_title_experience[i] and start_date[i] and end_date[i]:
                        insert_experience_query = """
                            INSERT INTO experiences (user_id, company_name, job_title, start_date, end_date, description)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute(insert_experience_query, (user_id, company_name[i], job_title_experience[i], start_date[i], end_date[i], description_experience[i]))
                        connection.commit()

                # Update education details
                school_name = request.form.getlist('school_name')
                degree = request.form.getlist('degree')
                field_of_study = request.form.getlist('field_of_study')
                start_date_edu = request.form.getlist('start_date_edu')
                end_date_edu = request.form.getlist('end_date_edu')
                description_education = request.form.getlist('description_education')

                for i in range(len(school_name)):
                    if school_name[i] and degree[i] and field_of_study[i] and start_date_edu[i] and end_date_edu[i]:
                        insert_education_query = """
                            INSERT INTO education (user_id, school_name, degree, field_of_study, start_date, end_date, description)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute(insert_education_query, (user_id, school_name[i], degree[i], field_of_study[i], start_date_edu[i], end_date_edu[i], description_education[i]))
                        connection.commit()

                flash('User details updated successfully', 'success')

            # Fetch user information
            cursor.execute('SELECT * FROM admin WHERE admin_id = %s', (user_id,))
            user = cursor.fetchone()

            # Fetch experience information
            cursor.execute('SELECT * FROM experiences WHERE user_id = %s', (user_id,))
            experience = cursor.fetchall()

            # Fetch education information
            cursor.execute('SELECT * FROM education WHERE user_id = %s', (user_id,))
            education = cursor.fetchall()

            cursor.close()
            connection.close()

            return render_template('admin_resume_1.html', user=user, experience=experience, education=education)
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
            if connection:
                connection.rollback()
            flash('An error occurred. Please try again later.', 'danger')
        finally:
            if connection:
                connection.close()
    return redirect(url_for('login'))

@app.route('/admin/edit_resume', methods=['GET', 'POST'])
def edit_resume():
    if 'loggedin' in session:
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            admin_id = session['userid']

            if request.method == 'POST':
                # Personal details
                first_name = request.form.get('first_name', '')
                last_name = request.form.get('last_name', '')
                job_title = request.form.get('job_title', '')
                description = request.form.get('description', '')
                profile_image = request.files.get('profile_image')
                email = request.form.get('email', '')
                phone = request.form.get('phone', '')
                address = request.form.get('address', '')
                summary = request.form.get('summary', '')

                update_query = """
                    UPDATE admin 
                    SET first_name = %s, last_name = %s, job_title = %s, description = %s, email = %s, phone = %s, address = %s, summary = %s 
                    WHERE admin_id = %s
                """
                cursor.execute(update_query, (first_name, last_name, job_title, description, email, phone, address, summary, admin_id))
                connection.commit()

                if profile_image and allowed_file(profile_image.filename):
                    filename = secure_filename(profile_image.filename)
                    profile_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                    cursor.execute('UPDATE admin SET profile_image = %s WHERE admin_id = %s', (filename, admin_id))
                    connection.commit()

                # Update experience details
                for key in request.form.keys():
                    if key.startswith('exp_title_'):
                        exp_id = key.split('_')[-1]
                        exp_title = request.form.get(f'exp_title_{exp_id}')
                        exp_company = request.form.get(f'exp_company_{exp_id}')
                        exp_start_date = request.form.get(f'exp_start_date_{exp_id}')
                        exp_end_date = request.form.get(f'exp_end_date_{exp_id}')
                        exp_description = request.form.get(f'exp_description_{exp_id}')

                        update_exp_query = """
                            UPDATE experiences
                            SET title = %s, company_name = %s, start_date = %s, end_date = %s, description = %s
                            WHERE id = %s AND user_id = %s
                        """
                        cursor.execute(update_exp_query, (exp_title, exp_company, exp_start_date, exp_end_date, exp_description, exp_id, admin_id))
                        connection.commit()

                # Update education details
                for key in request.form.keys():
                    if key.startswith('edu_school_'):
                        edu_id = key.split('_')[-1]
                        edu_school = request.form.get(f'edu_school_{edu_id}')
                        edu_degree = request.form.get(f'edu_degree_{edu_id}')
                        edu_start_date = request.form.get(f'edu_start_date_{edu_id}')
                        edu_end_date = request.form.get(f'edu_end_date_{edu_id}')
                        edu_description = request.form.get(f'edu_description_{edu_id}')

                        update_edu_query = """
                            UPDATE education
                            SET school_name = %s, degree = %s, start_date = %s, end_date = %s, description = %s
                            WHERE id = %s AND user_id = %s
                        """
                        cursor.execute(update_edu_query, (edu_school, edu_degree, edu_start_date, edu_end_date, edu_description, edu_id, admin_id))
                        connection.commit()

                flash('Resume updated successfully!', 'success')

            # Fetch existing details
            cursor.execute('SELECT * FROM admin WHERE admin_id = %s', (admin_id,))
            user = cursor.fetchone()

            cursor.execute('SELECT * FROM experiences WHERE user_id = %s', (admin_id,))
            experiences = cursor.fetchall()

            cursor.execute('SELECT * FROM education WHERE user_id = %s', (admin_id,))
            education = cursor.fetchall()

            return render_template('edit_resume.html', user=user, experiences=experiences, education=education)
        except mysql.connector.Error as e:
            print("Error executing SQL query:", e)
            if connection:
                connection.rollback()
            flash('An error occurred. Please try again later.', 'danger')
        finally:
            if connection:
                connection.close()
    return redirect(url_for('login'))


# Route for logging out
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)



               
                