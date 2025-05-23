from flask import Flask, request, jsonify
import re 
from flask_mysqldb import MySQL
from flask_cors import CORS

app = Flask(__name__)
mysql = MySQL(app)
CORS (app, resources={r"/*":{"origins": "http://localhost:3000"}})

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "ETM-System"




@app.route("/api/hello", methods=["GET"])
def hello():
    return jsonify(message="hello Pakistan")
#--__--__--__--__--__--__--__--__--__--__--__--__--__--__Register--__--__--__--__--__--__--__--__--__--__--__--__--__--__    
def is_valid_email(email):
    return re.match(r".+@.+\..+", email) is not None

@app.route("/api/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        
        full_name = data.get("full_name")
        email = data.get("email")
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        # Check if email is valid
        if not is_valid_email(email):
            return jsonify({"message": "Invalid email", "status": "error"}), 400

        # Password Match Validation
        if password != confirm_password:
            return jsonify({"message": "Passwords do not match", "status": "error"}), 400

        cursor = mysql.connection.cursor()
        query = "INSERT INTO register (full_name, email, password, confirm_password) VALUES(%s, %s, %s, %s)"
        cursor.execute(query, (full_name, email, password, confirm_password))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"message": "User registered successfully", "status": "success"})

    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500
#--__--__--__--__--__--__--__--__--__--__--__--__--__--__Login--__--__--__--__--__--__--__--__--__--__--__--__--__--__    

def is_valid_email(email):
     return re.match(r".+@.+\..+", email) is not None
 
@app.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")

        # Email validation
        if not is_valid_email(email):
            return jsonify({"message": "Invalid email", "status": "error"}), 400

        # Get user from DB
        cursor = mysql.connection.cursor()
        query = "SELECT email, password FROM register WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            db_email, db_password = user

            # Password match
            if password == db_password:
                return jsonify({"message": "Login successful", "status": "success"})
            else:
                return jsonify({"message": "Incorrect password", "status": "error"}), 401
        else:
            return jsonify({"message": "User not found", "status": "error"}), 404

    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500

#--__--__--__--__--__--__--__--__--__--__--__--__--__--__Expensive API--__--__--__--__--__--__--__--__--__--__--__--__--__--__    
@app.route("/api/expens", methods=["POST"])     
def expens():
    try: 
        data = request.get_json()
        
        expens_name = data.get("expens_name")
        price = float(data.get("price"))
        quantity = int(data.get("quantity"))
        
        # Check for required fields
        if not expens_name or price is None or quantity is None:
            return jsonify({"error": "All fields (expens_name, price, quantity) are required."}), 400

        total_price = price * quantity 
        one_quantity = price
        total_quantity = one_quantity


        cursor = mysql.connection.cursor()
        query = "INSERT INTO expens (expens_name, price, quantity) VALUES(%s, %s, %s)"
        cursor.execute(query, (expens_name, price, quantity))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({
            "message": "Expense added successfully",
            "id" : id,
            "total_price": total_price,
            "one_quantity" :price,
            "total_quantity": total_quantity
        })

    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500

#--__--__--__--__--__--__--__--__--__--__--__--__--__--__Expensive(UPDATE) API--__--__--__--__--__--__--__--__--__--__--__--__--__--__    
@app.route("/api/update/expens/<int:id>", methods=["PUT"])
def update_expens(id):
    try:
        data = request.get_json()
        
        quantity = data.get("quantity")
        price = data.get("price")
        
        cursor = mysql.connection.cursor()
        query = """
            UPDATE expens
            SET quantity = %s, price = %s
            WHERE id = %s
        """
        cursor.execute(query, (quantity, price, id))
        mysql.connection.commit()
        cursor.close()

        return jsonify({
            "message": "Your expense is updated",
            "quantity": quantity,
            "price": price
        })
        
    except Exception as e:
        return jsonify({"error": str(e)})
#--__--__--__--__--__--__--__--__--__--__--__--__--__--__Expensive(DELETE) API--__--__--__--__--__--__--__--__--__--__--__--__--__--__    

@app.route("/api/delete/expens/<int:id>", methods=["DELETE"])
def delete_expens(id):
    try:
        cursor = mysql.connection.cursor()
        query = """DELETE 
                FROM expens
                    WHERE id = %s
                """
        cursor.execute(query,(id,))
        cursor.close()
        cursor =  mysql.connection.commit()
        return jsonify({
            "messasge": "delete sucessful ",
            "id" : id
            }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
#--__--__--__--__--__--__--__--__--__--__--__--__--__--__Expensive(GET) API--__--__--__--__--__--__--__--__--__--__--__--__--__--__    
@app.route("/api/get/expens", methods=["GET"])
def get_expens():
    try:
        cursor = mysql.connection.cursor()
        expens_name = request.args.get("expens_name")
        price = request.args.get("price")
        quantity = request.args.get("quantity")

        query = """SELECT * FROM expens WHERE 1=1"""
        values = []
        if expens_name:
            query += " AND expens_name = %s"
            values.append(expens_name)
        if price:
            query += " AND price = %s"
            values.append(price)
        if quantity:
            query += " AND quantity = %s"
            values.append(quantity)

        cursor.execute(query, values)
        result = cursor.fetchall()
        return jsonify({"message": "GET these all data",
                        "result" :result })
    except Exception as e:
        return jsonify({"error": str(e)})
#--__--__--__--__--__--__--__--__--__--__--__--__--__--__InCome(Add) API--__--__--__--__--__--__--__--__--__--__--__--__--__--__    
@app.route("/api/add/income", methods= ["POST"])
def add_incom():
    try:
        data  =  request.get_json()
        
        source = data.get("source")
        amount = float(data.get("amount"))
        description = data.get("description")
        
        
        cursor = mysql.connection.cursor()
        query = "INSERT INTO income (source, amount,description) VALUES(%s, %s, %s)"
        cursor.execute(query,(source, amount,description ))
        cursor = mysql.connection.commit()
        return jsonify({
            "message": "Data is added",
            "ic_source" : source,
            "amount": amount,
            "description" : description}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
#--__--__--__--__--__--__--__--__--__--__--__--__--__--__InCome(UPDATE) API--__--__--__--__--__--__--__--__--__--__--__--__--__--__    
@app.route("/api/update/income/<int:id>", methods=["PUT"])
def update_income(id):
    try: 
        data = request.get_json()
        
        source = data.get("source")
        amount = data.get("amount")
        description = data.get("description")
        
        cursor = mysql.connection.cursor()
        query = """
            UPDATE income 
            SET source = %s, amount = %s, description = %s
            WHERE id = %s
        """
        cursor.execute(query, (source, amount, description, id))
        mysql.connection.commit()
        cursor.close()

        return jsonify({
            "message": "Income data is updated.",
            "source": source,
            "amount": amount,
            "description": description
        })

    except Exception as e:
        return jsonify({"error": str(e)})
#--__--__--__--__--__--__--__--__--__--__--__--__--__--__InCome(DELETE) API--__--__--__--__--__--__--__--__--__--__--__--__--__--__    
@app.route("/api/delete/income/<int:id>", methods=["DELETE"])
def delete_income(id):
    try:
        cursor = mysql.connection.cursor()
        query = "DELETE FROM income WHERE id =%s"
        cursor.execute(query,(id,))
        cursor = mysql.connection.commit()
        return jsonify({"message": "Income is deleted successful.."})
    except Exception as e:
        return jsonify({"error": str(e)})
#--__--__--__--__--__--__--__--__--__--__--__--__--__--__InCome(GET) API--__--__--__--__--__--__--__--__--__--__--__--__--__--__    
@app.route("/api/get/income", methods= ["GET"])
def get_income():
    try:
        cursor = mysql.connection.cursor()

        source = request.args.get("source")
        amount = request.args.get("amount")
        description = request.args.get("description")

        query = "SELECT * FROM income WHERE 1=1"
        values = []
        if source:
            query += " AND source = %s"
            values.append(source)
        if amount:
            query += " AND amount = %s"
            values.append(amount)
        if description:
            query += " AND description = %s"
            values.append(description)
        
        cursor.execute(query, values)
        result = cursor.fetchall()
        return jsonify({"message": "Data is get sucess",
                        "result": result})
    except Exception as e:
        return jsonify({"error": str(e)})
#--__--__--__--__--__--__--__--__--__--__--__--__--__--__Balance(POST) API--__--__--__--__--__--__--__--__--__--__--__--__--__--__    

@app.route("/api/add/balance", methods=["POST"])
def add_balance():
    try:
        data  =  request.get_json()
        
        total_income = data.get("total_income")
        total_expens = data.get("total_expens")
        current_balance = data.get("current_balance")
        
        cursor = mysql.connection.cursor()
        query = "INSERT INTO balance (total_income, total_expens, current_balance) VALUES(%s, %s, %s)"
        cursor.execute(query, (total_income, total_expens, current_balance))  # ✅ Values passed correctly
        mysql.connection.commit()  # ✅ No need to assign commit() to cursor
        cursor.close()
        
        return jsonify({"message": "Data is added successfully."})
    except Exception as e:
        return jsonify({"error": str(e)})
#--__--__--__--__--__--__--__--__--__--__--__--__--__--__Balance(GET) API--__--__--__--__--__--__--__--__--__--__--__--__--__--__    
@app.route("/api/get/balance", methods = ["GET"])
def get_balance():
    try:
        cursor = mysql.connection.cursor()
        total_income = request.args.get("total_income")
        total_expens = request.args.get("total_expens")
        current_balance = request.args.get("current_balance")

        query = "SELECT * FROM balance WHERE 1=1"
        values = []
        if total_income:
            query += " AND total_income = %s"
            values.append(total_income)
        if total_expens:
            query += " AND total_expens = %s"
            values.append(total_expens)
        if current_balance:
            query += " AND current_balance = %s"
            values.append(current_balance)

        cursor.execute(query, values)
        result = cursor.fetchall()
        return jsonify({
            "message": "Your are get all data",
            'result' : result
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
#--__--__--__--__--__--__--__--__--__--__--__--__--__--__Balance(UPDATE) API--__--__--__--__--__--__--__--__--__--__--__--__--__--__    
@app.route("/api/update/balance/<int:id>", methods=["PUT"])
def update_balance(id):
    try:
        data = request.get_json()
        
        total_income = data.get("total_income")
        total_expens = data.get("total_expens")
        current_balance = data.get("current_balance")
        
        
        cursor = mysql.connection.cursor()
        query = """
                UPDATE balance
                SET total_income = %s, total_expens=%s, current_balance = %s
                WHERE id= %s"""
        cursor.execute(query, (total_income, total_expens, current_balance,id))
        cursor = mysql.connection.commit()
        return jsonify({
            "message": "You are update his balance.",
            
            
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
                
#--__--__--__--__--__--__--__--__--__--__--__--__--__--__Balance(DELETE) API--__--__--__--__--__--__--__--__--__--__--__--__--__--__    
@app.route("/api/delete/balance/<int:id>", methods=["DELETE"])
def delete_balance(id):
    try:
        cursor = mysql.connection.cursor()
        query = "DELETE FROM balance WHERE id=%s"
        cursor.execute(query,(id,))
        cursor = mysql.connection.commit()
        return jsonify({"message": "blanace data is deleted. "})
    except Exception as e:
        return jsonify({"error": str(e)})
    
if __name__ == '__main__':
    app.run( host='0.0.0.0', port=5000,debug=True)
    
      