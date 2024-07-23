from flask import *
import mysql.connector

app = Flask(__name__)

try:
    conn=mysql.connector.connect(
    host='localhost',
    user="root",
    password='95506@Mahi',
    database='flask_mysql_db'
        )
    cursor=conn.cursor()
except mysql.connector.Error as e:
    print("Error connecting to mysql database:",e)

@app.route('/')
@app.route('/index', methods=['GET','POST']) 
def index():
    return render_template('index.html', methods=['GET','POST'])

@app.route('/about',methods=['GET','POST'])
def about():
    return render_template('about.html')

@app.route('/service',methods=['GET','POST'])
def service():
    return render_template('service.html')

@app.route('/doctors',methods=['GET','POST'])
def doctors():
    return render_template('doctors.html')

@app.route('/contact',methods=['GET','POST'])
def contact():
    return render_template('contact.html')

@app.route('/display',methods=['POST','GET'])
def display():
    if request.method=='POST':  
        fname=request.form['fname']
        lname=request.form['lname']
        email=request.form['email']
        mobile=request.form['mobile']
        gender=request.form['gender']
        date=request.form['date']
        comment=request.form['comment']
        try:
          cursor.execute("INSERT INTO details(fname,lname,email,mobile,gender,date,comment) VALUES (%s, %s,%s,%s,%s,%s,%s)", (fname,lname,email,mobile,gender,date,comment))
          conn.commit()
          return redirect(url_for('appointment')) 
        except mysql.connector.Error as er:
          print('system error',er)
        return redirect(url_for('appointment'))
    else:
       pass
@app.route("/appointment")
def appointment():
   try:
      cursor.execute("select * from details ")
      value = cursor.fetchall()
      return render_template('dashboard.html',data=value)
   except mysql.connector.Error as e:
      print("system error",e)
      return"Error fetching data from the database"
@app.route('/update/<id>')
def update(id):
    cursor.execute('SELECT * FROM details WHERE id = %s', (id,))
    value = cursor.fetchone()
    return render_template('edit.html', data=value)

@app.route('/delete/<id>')
def delete(id):
    try:
        cursor.execute('DELETE FROM details WHERE id = %s', (id,))
        return redirect(url_for('appointment'))
    except mysql.connector.Error as e:
      print("system error",e)
      return"Error fetching data from the database"

@app.route('/edit_section', methods=['POST', 'GET'])
def edit_section():
    if request.method == 'POST':
        try:
            id = request.form['id']
            fname = request.form['fname']
            lname = request.form['lname']
            email = request.form['email']
            mobile = request.form['mobile']
            gender = request.form['gender']
            date = request.form['date']
            comment = request.form['comment']
            update_query = """
                UPDATE details 
                SET fname=%s, lname=%s, email=%s, mobile=%s, gender=%s, date=%s, comment=%s 
                WHERE id=%s
            """
            cursor.execute(update_query, (fname, lname, email, mobile, gender,date, comment, id))
            conn.commit()
            return redirect(url_for('appointment'))
        except mysql.connector.Error as er:
            print('System error:', er)
            return "Database error during update"
    else:
        return "Invalid request method"

if __name__ == '__main__':
    app.run(debug=True)
