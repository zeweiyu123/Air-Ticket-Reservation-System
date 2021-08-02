#!C:/Users/lx615/AppData/Local/Programs/Python/Python38-32/python

#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect, flash
import mysql.connector
import json
import datetime
import decimal

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = mysql.connector.connect(host='localhost',
                       user='root',
                       password='',
                       database='air')


def check_input(x):
    assert type(x) == str
    if "'" not in x:
        return x
    y = ''
    for i in x:
        if i == "'":
            y += "''"
        else:
            y += i
    return y
    
####################################################################################
#PUBLIC
@app.route('/')
def publicHome():
    return render_template('publicHome.html')
    
@app.route('/publicsearchstatus', methods=['GET', 'POST'])
def publicsearchstatus():
    airline_name = check_input(request.form['airline_name'])
    departure_date = request.form['departure_date']
    arrival_date = request.form['arrival_date']
    flight_num = request.form['flight_num']

    cursor = conn.cursor()
    query = "SELECT * \
            FROM public_search_flight \
            WHERE flight_num = if (\'{}\' = '', flight_num, \'{}\') and \
                    date(departure_time) = if (\'{}\' = '', date(departure_time), \'{}\') and \
                    date(arrival_time) = if (\'{}\' = '', date(arrival_time), \'{}\') and \
                    airline_name = if (\'{}\' = '', airline_name, \'{}\') \
            ORDER BY airline_name, flight_num"
    cursor.execute(query.format(flight_num, flight_num, arrival_date, arrival_date, departure_date, departure_date, airline_name, airline_name))
    data = cursor.fetchall()
    cursor.close()
    
    if (data): # has data
        # upcoming_flights = session['upcoming_flights']
        return render_template('publicHome.html', statuses=data)
    else: # does not have data
        error = 'Sorry Flight not Found!'
        return render_template('publicHome.html', error2=error)

@app.route('/publicsearchflight', methods=['GET', 'POST'])
def publicSearchFlight():
    departure_city = check_input(request.form['departure_city'])
    departure_airport = check_input(request.form['departure_airport'])
    arrival_city = check_input(request.form['arrival_city'])
    arrival_airport = check_input(request.form['arrival_airport'])
    departure_date = request.form['departure_date']
    arrival_date = request.form['arrival_date']

    cursor = conn.cursor()
    query = "SELECT airline_name, flight_num, departure_city, departure_airport, departure_time, arrival_city, arrival_airport, arrival_time, price, airplane_id \
            FROM public_search_flight \
            WHERE departure_airport = if (\'{}\' = '', departure_airport, \'{}\') AND \
                    arrival_airport = if (\'{}\' = '', arrival_airport, \'{}\') AND \
                    status = 'upcoming' AND \
                    departure_city = if (\'{}\' = '', departure_city, \'{}\') AND \
                    arrival_city = if (\'{}\' = '',arrival_city, \'{}\') AND \
                    date(departure_time) = if (\'{}\' = '',date(departure_time), \'{}\') AND \
                    date(arrival_time) = if (\'{}\' = '',date(arrival_time), \'{}\') \
            ORDER BY airline_name, flight_num"
    cursor.execute(query.format(departure_airport, departure_airport, arrival_airport, arrival_airport, departure_city, departure_city, arrival_city, arrival_city, departure_date, departure_date, arrival_date, arrival_date))
    data = cursor.fetchall()
    cursor.close()
    
    if (data): # has data
        return render_template('publicHome.html', upcoming_flights=data)
    else: # does not have data
        error = 'Sorry ... Cannot find this flight!'
        return render_template('publicHome.html', error1=error)

        
        
###############################################################################
#Customer
###############################################################################

@app.route('/customerlogin')
def customerlogin():
    return render_template('customerlogin.html')
    
@app.route('/customerregister')
def customerregister():
    return render_template('customerregister.html')

@app.route('/customerlogincheck', methods=['GET', 'POST'])
def customerlogincheck():
    if 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        db_email=check_input(email)
        password = request.form['password']

        cursor = conn.cursor()
        query = "SELECT * FROM customer WHERE email = \'{}\' and password = md5(\'{}\')"
        cursor.execute(query.format(email, password))
        data = cursor.fetchone()
        cursor.close()
        if(data):
            session['email'] = email
            cursor = conn.cursor()
            query = "SELECT ticket_id, airline_name, airplane_id, flight_num, D.airport_city, departure_airport, A.airport_city, arrival_airport, departure_time, arrival_time, status \
                FROM flight NATURAL JOIN purchases NATURAL JOIN ticket, airport as D, airport as A\
                    WHERE customer_email = \'{}\' and status = 'upcoming' and \
                    D.airport_name = departure_airport and A.airport_name = arrival_airport"
            cursor.execute(query.format(db_email))
            DATA = cursor.fetchall()
            cursor.close()
            return render_template('customerhome.html', db_email=email, emailname=email.split('@')[0], flights=DATA)
        else:
            #returns an error message to the html page
            error = 'Invalid email or password. Please try again!'
            return render_template('customerlogin.html', error=error)
    else:
        session.clear()
        return render_template('404.html')

# Authenticates the register
@app.route('/customerregistercheck', methods=['GET', 'POST'])
def customerregistercheck():
    if 'email' in request.form and \
        'name' in request.form and \
        'password' in request.form and \
        'building_number' in request.form and \
        'street' in request.form and \
        'city' in request.form and \
        'state' in request.form and \
        'phone_number' in request.form and \
        'passport_number' in request.form and \
        'passport_expiration' in request.form and \
        'passport_country' in request.form and \
        'date_of_birth' in request.form:
        
        email = request.form['email']
        db_email=check_input(request.form['email'])
        name = request.form['name']
        db_name = check_input(name)
        password = request.form['password']
        building_number = check_input(request.form['building_number'])
        street = check_input(request.form['street'])
        city = check_input(request.form['city'])
        state = check_input(request.form['state'])
        phone_number = request.form['phone_number']
        passport_number = check_input(request.form['passport_number'])
        passport_expiration = request.form['passport_expiration']
        passport_country = check_input(request.form['passport_country'])
        date_of_birth = request.form['date_of_birth']

        cursor = conn.cursor()
        query = "SELECT * FROM customer WHERE email = \'{}\'"
        cursor.execute(query.format(email))
        data = cursor.fetchone()
        if(data):
            cursor.close()
            error = "This user already exists"
            return render_template('customerregister.html', error = error)
        else:
            insert = "INSERT INTO customer VALUES(\'{}\', \'{}\', md5(\'{}\'), \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\')"
            cursor.execute(insert.format(email, db_name, password, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth))
            conn.commit()
            query = "SELECT ticket_id, airline_name, airplane_id, flight_num, \
                D.airport_city, \
                departure_airport, A.airport_city, arrival_airport, departure_time, arrival_time, status \
                    FROM flight NATURAL JOIN purchases NATURAL JOIN ticket, airport as D, airport as A\
                        WHERE customer_email = \'{}\' and status = 'upcoming' and \
                        D.airport_name = departure_airport and A.airport_name = arrival_airport"
            cursor.execute(query.format(email))
            DATA = cursor.fetchall()
            cursor.close()
            flash("You are logged in")
            session['email'] = email
            return render_template('customerhome.html', db_email=email, emailname=email.split('@')[0], flights=DATA)
    else:
        session.clear()
        return render_template('404.html')

@app.route('/customerhome')
def customerhome():
    if session.get('email'):
        email = check_input(session['email'])

        cursor = conn.cursor()
        query = "SELECT ticket_id, airline_name, airplane_id, flight_num, \
            D.airport_city, \
            departure_airport, A.airport_city, arrival_airport, departure_time, arrival_time, status \
                FROM flight NATURAL JOIN purchases NATURAL JOIN ticket, airport as D, airport as A\
                    WHERE customer_email = \'{}\' and status = 'upcoming' and \
                    D.airport_name = departure_airport and A.airport_name = arrival_airport"
        cursor.execute(query.format(email))
        data1 = cursor.fetchall()
        cursor.close()
        return render_template('customerhome.html', email=email, emailname=email.split('@')[0], flights=data1)
    else:
        session.clear()
        return render_template('404.html')
        
@app.route('/customersearchpurchase')
def customersearchpurchase():
    if session.get('email'):
        email = session['email']
        return render_template('customerSearchPurchase.html', email=email, emailname=email.split('@')[0])
    else:
        session.clear()
        return render_template('404.html')
        
@app.route('/customersearchflight', methods=['GET', 'POST'])
def customerSearchFlight():
    if session.get('email'):
        email = session['email']
        db_email = check_input(email)
        departure_city = check_input(request.form['departure_city'])
        departure_airport = check_input(request.form['departure_airport'])
        arrival_city = check_input(request.form['arrival_city'])
        arrival_airport = check_input(request.form['arrival_airport'])
        departure_date = request.form['departure_date']
        arrival_date = request.form['arrival_date']

        cursor = conn.cursor()
        query = "SELECT airline_name, airplane_id, flight_num, D.airport_city, departure_airport, A.airport_city, arrival_airport, departure_time, arrival_time, price, status\
                FROM airport as D, flight, airport AS A \
                WHERE D.airport_city = if (\'{}\' = '',D.airport_city, \'{}\') and \
                        D.airport_name = departure_airport and \
                        departure_airport = if (\'{}\' = '', departure_airport, \'{}\') and \
                        A.airport_city = if (\'{}\' = '', A.airport_city, \'{}\')and \
                        A.airport_name = arrival_airport and \
                        arrival_airport =  if (\'{}\' = '', arrival_airport, \'{}\')and \
                        date(departure_time) = if (\'{}\' = '', date(departure_time), \'{}\')and \
                        date(arrival_time) =  if (\'{}\' = '', date(arrival_time), \'{}\') \
                        ORDER BY airline_name, flight_num"
        cursor.execute(query.format(departure_city,departure_city,departure_airport,departure_airport, arrival_city, arrival_city, arrival_airport, arrival_airport, departure_date, departure_date, arrival_date,arrival_date))
        data = cursor.fetchall()
        cursor.close()
        
        if (data):
            return render_template('customerSearchPurchase.html', email = email, emailname=email.split('@')[0], flights=data)
        else:
            error = 'Flight does not exist, sorry!'
            return render_template('customerSearchPurchase.html', email = email, emailname=email.split('@')[0], error1=error)
    else:
        session.clear()
        return render_template('404.html')

@app.route('/customertickets', methods=['GET', 'POST'])
def customerTickets():
    if session.get('email'):
        email = session['email']
        db_email = check_input(email)
        airline_name = check_input(request.form['airline_name'])
        flight_num = request.form['flight_num']

        cursor = conn.cursor()
        query = "SELECT * \
                FROM flight \
                WHERE airline_name = \'{}\' AND flight_num = \'{}\'"
        cursor.execute(query.format(airline_name, flight_num))
        data = cursor.fetchall()
        cursor.close()

        if(data):
            cursor = conn.cursor()
            query_id = "SELECT ticket_id \
                        FROM ticket \
                        ORDER BY ticket_id DESC \
                        LIMIT 1"
            cursor.execute(query_id)
            ticket_id_data = cursor.fetchone()
            new_ticket_id = int(ticket_id_data[0]) + 1
            # first insert into ticket
            insertion1 = "INSERT INTO ticket VALUES (\'{}\', \'{}\', \'{}\')"
            cursor.execute(insertion1.format(new_ticket_id, airline_name, flight_num))
            # then insert into purchases
            insertion = "INSERT INTO purchases VALUES (\'{}\', \'{}\', NULL, CURDATE())"
            cursor.execute(insertion.format(new_ticket_id, db_email))
            conn.commit()
            cursor.close()
            message1 = 'Successful!'
            return render_template('customerSearchPurchase.html', email = email, message1 = message1)
        else:
            error = 'No ticket remaining, sorry!'
            return render_template('customerSearchPurchase.html', error2=error, email = email, emailname=email.split('@')[0])
    else:
        session.clear()
        return render_template('404.html')

@app.route('/customerspending', methods=['POST', 'GET'])
def customerspending():
    if session.get('email'):
        email = session['email']
        db_email = check_input(email)

        # show total spending in the past period of time
        duration = request.form.get("duration")
        if duration is None:
            duration = "365"
        cursor = conn.cursor()
        query = "select sum(price)\
                    from customer_spending \
                    where customer_email = \'{}\' and (purchase_date between DATE_ADD(NOW(), INTERVAL -\'{}\' DAY) and NOW())"
        cursor.execute(query.format(db_email, duration))
        total_spending = cursor.fetchone()
        cursor.close()

        # show month-wise spending in the past 6 months
        period = request.form.get("period")
        if period is None:
            period = '6'
        today = datetime.date.today()
        past_day = today.day
        past_month = (today.month - int(period)) % 12
        if past_month == 0:
            past_month = 12
        past_year = today.year + ((today.month - int(period) - 1) // 12)
        past_date = datetime.date(past_year, past_month, past_day) # the day 6 months ago

        cursor = conn.cursor()
        query2 = "select year(purchase_date) as year, month(purchase_date) as month, sum(price) as monthly_spending \
                    from customer_spending \
                    where customer_email = \'{}\' and purchase_date >= \'{}\' \
                    group by year(purchase_date), month(purchase_date)"
        cursor.execute(query2.format(db_email, past_date))
        monthly_spending_data = cursor.fetchall()
        cursor.close()

        months = []
        monthly_spendings = []
        for i in range(int(period)):
            month = (past_date.month + i + 1) % 12
            if month == 0:
                month = 12
            year = past_date.year + ((past_date.month + i) // 12)
            flag = False
            for one_month in monthly_spending_data:
                if one_month[0] == year and one_month[1] == month:
                    flag = True
                    break
            if flag:
                monthly_spendings.append(int(one_month[2]))
            else:
                monthly_spendings.append(0)
            months.append(str(year)+'-'+str(month))

        return render_template('customerSpending.html', email=email, emailname=email.split('@')[0], total_spending=total_spending[0], duration=duration, period=period, months=months, monthly_spendings=monthly_spendings)
    else:
        session.clear()
        return render_template('404.html')




###############################################################################
#Booking Agent
###############################################################################
@app.route('/agentlogin')
def agentlogin():
    return render_template('agentlogin.html')
    
@app.route('/agentregister')
def agentregister():
    return render_template('agentregister.html')
    
@app.route('/agenthome')
def agenthome():
    if session.get('agentemail'):
        email = session['agentemail']
        db_email = check_input(email)
            
        cursor = conn.cursor()
        query1 = "SELECT booking_agent_id FROM booking_agent WHERE email = \'{}\'"
        cursor.execute(query1.format(db_email))
        data = cursor.fetchone()
        query2 = "SELECT * FROM agent_view_flight WHERE email = \'{}\'"
        cursor.execute(query2.format(db_email))
        DATA = cursor.fetchall()
        cursor.close()
        return render_template('agenthome.html',emailname=email.split('@')[0], flights=DATA, booking_agent_id=data)
    else:
        session.clear()
        return render_template('404.html')
        
        
@app.route('/agentlogincheck', methods=['GET', 'POST'])
def agentlogincheck():
    if "email" in request.form and 'password' in request.form:
        email = request.form['email']
        db_email = check_input(email)
        password = request.form['password']

        cursor = conn.cursor()
        query = "SELECT * FROM booking_agent WHERE email = \'{}\' and password = md5(\'{}\')"
        cursor.execute(query.format(db_email, password))
        data = cursor.fetchone()
        cursor.close()
        if(data):
            cursor = conn.cursor()
            query1 = "SELECT booking_agent_id FROM booking_agent WHERE email = \'{}\'"
            cursor.execute(query1.format(db_email))
            data = cursor.fetchone()
            query2 = "SELECT * FROM agent_view_flight WHERE email = \'{}\'"
            cursor.execute(query2.format(db_email))
            DATA = cursor.fetchall()
            cursor.close()
            session['agentemail'] = email
            return render_template('agenthome.html', email=email, emailname=email.split('@')[0], flights=DATA, booking_agent_id=data)
        else:
            error = 'Invalid email or password. Please try again!'
            return render_template('agentlogin.html', error=error)
    else:
        session.clear()
        return render_template('404.html')
        
@app.route('/agentregistercheck', methods=['GET', 'POST'])
def agentregistercheck():
    if "email" in request.form and 'password' in request.form and 'booking_agent_id' in request.form:
        email = request.form['email']
        db_email = check_input(email)
        password = request.form['password']
        booking_agent_id = request.form['booking_agent_id']

        cursor = conn.cursor()
        query = "SELECT * FROM booking_agent WHERE email = \'{}\'"
        cursor.execute(query.format(db_email))
        data = cursor.fetchone()
        if(data):
            cursor.close()
            error = "This user already exists"
            return render_template('agentregister.html', error = error)
        else:
            ins = "INSERT INTO booking_agent VALUES(\'{}\', md5(\'{}\'), \'{}\')"
            cursor.execute(ins.format(db_email, password, booking_agent_id))
            conn.commit()
            query1 = "SELECT booking_agent_id FROM booking_agent WHERE email = \'{}\'"
            cursor.execute(query1.format(db_email))
            data1 = cursor.fetchone()
            # get view_my_flights info from db
            query = "SELECT * FROM agent_view_flight WHERE email = \'{}\'"
            cursor.execute(query.format(db_email))
            data2 = cursor.fetchall()
            cursor.close()
            session['agentemail'] = email
            flash("Successful!")
            return render_template('agenthome.html', email=email, emailname=email.split('@')[0], flights=data2, booking_agent_id=data1)
    else:
        session.clear()
        return render_template('404.html')
        
@app.route('/agentsearchpurchase')
def agentsearchpurchase():
    if session.get('agentemail'):
        email = session['agentemail']
        return render_template('agentSearchPurchase.html', emailname=email.split('@')[0], )
    else:
        session.clear()
        return render_template('404.html')

@app.route('/agentcommission', methods=['POST', 'GET'])
def agentCommission():
    if session.get('agentemail'):
        email = session['agentemail']
        db_email = check_input(email)

        cursor = conn.cursor()
        duration = request.form.get("duration")
        if duration is None:
            duration = "30"
        query = 'select sum(ticket_price * 0.1), avg(ticket_price * 0.1), count(ticket_price * 0.1) from agent_commission where email = \'{}\' and (purchase_date between DATE_ADD(NOW(), INTERVAL -\'{}\' DAY) and NOW())'
        cursor.execute(query.format(db_email, duration))
        commission_data = cursor.fetchone()
        total_com, avg_com, count_ticket = commission_data
        cursor.close()
        return render_template('agentCommission.html', emailname=email.split('@')[0], total_com=total_com, avg_com=avg_com, count_ticket=count_ticket, duration=duration)
    else:
        session.clear()
        return render_template('404.html')

@app.route('/agenttopcustomers')
def agenttopcustomers():
    if session.get('agentemail'):
        email = session['agentemail']
        db_email = check_input(email)

        cursor = conn.cursor()
        query = "select customer_email, count(ticket_id) \
                from agent_commission where email = \'{}\' and \
                datediff(CURDATE(), DATE(purchase_date)) < 183 \
                group by customer_email \
                order by count(ticket_id) desc"
        cursor.execute(query.format(db_email))
        ticket_data = cursor.fetchall()
        cursor.close()

        l = len(ticket_data)
        if l >= 5:
            ppl1 = [ticket_data[i][0] for i in range(5)]
            tickets = [ticket_data[i][1] for i in range(5)]
        else:
            ppl1 = [ticket_data[i][0] for i in range(l)]
            tickets = [ticket_data[i][1] for i in range(l)]
            for i in range(5 - l):
                ppl1.append(' ')
                tickets.append(0)
        
        cursor = conn.cursor()
        query2 = "select customer_email, sum(ticket_price) * 0.1 \
                from agent_commission where email = \'{}\' and \
                datediff(CURDATE(), DATE(purchase_date)) < 365 \
                group by customer_email \
                order by sum(ticket_price) desc"
        cursor.execute(query2.format(db_email))
        commission_data = cursor.fetchall()
        cursor.close()

        l2 = len(commission_data)
        if l2 >= 5:
            ppl2 = [commission_data[i][0] for i in range(5)]
            commissions = [commission_data[i][1] for i in range(5)]
        else:
            ppl2 = [commission_data[i][0] for i in range(l2)]
            commissions = [int(commission_data[i][1]) for i in range(l2)]
            for i in range(5 - l):
                ppl2.append(' ')
                commissions.append(0)
        return render_template('agentTopCustomers.html', email=email,emailname=email.split('@')[0], ppl1=ppl1, ppl2=ppl2, tickets=tickets, commissions=commissions)
    else:
        session.clear()
        return render_template('404.html')

@app.route('/agentsearchflight', methods=['GET', 'POST'])
def agentsearchflight():
    if session.get('agentemail'):
        email = session['agentemail']
        db_email = check_input(email)
        departure_city = check_input(request.form['departure_city'])
        departure_airport = check_input(request.form['departure_airport'])
        arrival_city = check_input(request.form['arrival_city'])
        arrival_airport = check_input(request.form['arrival_airport'])
        departure_date = request.form['departure_date']
        arrival_date = request.form['arrival_date']

        # validate booking agent email
        cursor = conn.cursor()
        query = "select booking_agent_id from booking_agent where email = \'{}\'"
        cursor.execute(query.format(db_email))
        agent_data = cursor.fetchone() # tuple (98765,)
        booking_agent_id = agent_data[0]
        cursor.close()

        if not (agent_data):
            agent_id_error = 'You are not a booking agent'
            return render_template('agentSearchPurchase.html', error1=agent_id_error)

        # booking agent email has been validated
        cursor = conn.cursor()
        query = "SELECT airplane_id, flight_num, D.airport_city, departure_airport, A.airport_city, arrival_airport, departure_time, arrival_time, status, price, airline_name \
                FROM airport as D, flight, airport AS A \
                WHERE D.airport_city = if (\'{}\' = '',D.airport_city, \'{}\') and \
                    D.airport_name = departure_airport and \
                    departure_airport = if (\'{}\' = '', departure_airport, \'{}\') and \
                    A.airport_city = if (\'{}\' = '', A.airport_city, \'{}\')and \
                    A.airport_name = arrival_airport and \
                    arrival_airport =  if (\'{}\' = '', arrival_airport, \'{}\')and \
                    date(departure_time) = if (\'{}\' = '', date(departure_time), \'{}\')and \
                    date(arrival_time) =  if (\'{}\' = '', date(arrival_time), \'{}\') \
                ORDER BY airline_name, flight_num"
        cursor.execute(query.format(departure_city, departure_city,departure_airport,departure_airport, arrival_city, arrival_city, arrival_airport, arrival_airport, departure_date, departure_date, arrival_date, arrival_date))
        data = cursor.fetchall()
        cursor.close()
        
        if (data): # has data
            return render_template('agentSearchPurchase.html', email=email, emailname=email.split('@')[0], flights=data)
        else: # does not have data
            error = 'Sorry no flight found!'
            return render_template('agentSearchPurchase.html', email=email, emailname=email.split('@')[0], error1=error)
    else:
        session.clear()
        return render_template('404.html')

@app.route('/agentbuytickets', methods=['GET', 'POST'])
def agentbuytickets():
    if session.get('agentemail'):
        email = session['agentemail']
        airline_name = check_input(request.form.get("airline_name"))
        db_email = check_input(email)
        flight_num = request.form.get("flight_num")
        customer_email = check_input(request.form['customer_email'])

        # validate booking agent email
        cursor = conn.cursor()
        query = "select booking_agent_id from booking_agent where email = \'{}\'"
        cursor.execute(query.format(db_email))
        agent_data = cursor.fetchone() # tuple (98765,)
        booking_agent_id = agent_data[0]
        cursor.close()

        if not (agent_data):
            agent_id_error = 'Not a booking agent'
            return render_template('agentSearchPurchase.html', error2=agent_id_error)

        # validate customer_email is registered
        cursor = conn.cursor()
        query = "select * from customer where email = \'{}\'"
        cursor.execute(query.format(customer_email))
        cus_data = cursor.fetchone()
        cursor.close()

        if not (cus_data):
            email_error = 'Not registered.'
            return render_template('agentSearchPurchase.html', error2=email_error)

        # customer_email is validated
        cursor = conn.cursor()
        query = "SELECT * \
                FROM flight \
                WHERE airline_name = \'{}\' AND flight_num = \'{}\'"
        cursor.execute(query.format(airline_name, flight_num))
        flight_data = cursor.fetchall()
        cursor.close()

        if not (flight_data):
            ticket_error = 'No ticket'
            return render_template('agentSearchPurchase.html', error2=ticket_error, email=email, emailname=email.split('@')[0])
        else:
            cursor = conn.cursor()
            # calc the new ticket id = biggest id + 1
            cursor = conn.cursor()
            query_id = "SELECT ticket_id \
                        FROM ticket \
                        ORDER BY ticket_id DESC \
                        LIMIT 1"
            cursor.execute(query_id)
            ticket_id_data = cursor.fetchone() # (74373,)
            new_ticket_id = int(ticket_id_data[0]) + 1
            # first insert into ticket
            ins1 = "INSERT INTO ticket VALUES (\'{}\', \'{}\', \'{}\')"
            cursor.execute(ins1.format(new_ticket_id, airline_name, flight_num))
            # then insert into purchases
            ins = "INSERT INTO purchases VALUES (\'{}\', \'{}\', \'{}\', CURDATE())"
            cursor.execute(ins.format(new_ticket_id, customer_email, booking_agent_id))
            conn.commit()
            cursor.close()
            message = 'Ticket bought successfully!'
            return render_template('agentSearchPurchase.html', message=message, email=email, emailname=email.split('@')[0])
    else:
        session.clear()
        return render_template('404.html')
        
###############################################################################
#Airline Staff
###############################################################################
@app.route('/stafflogin')
def stafflogin():
    return render_template("stafflogin.html")

@app.route('/staffregister')
def staffregister():
    return render_template("staffregister.html")
    
@app.route('/stafflogincheck',methods=['GET', 'POST'])
def stafflogincheck():
    if 'username' in request.form and 'password' in request.form:
        username=request.form['username']
        password=request.form['password']
        db_username=check_input(username)
        
        cursor=conn.cursor()
        query1="select username,airline_name,airplane_id,flight_num,departure_airport,departure_time,arrival_airport,arrival_time from flight natural join airline_staff where username=\'{}\' and status='upcoming' and datediff(CURDATE(),DATE(departure_time))<30"
        cursor.execute(query1.format(db_username))
        data1=cursor.fetchall()
        
        query2="select * from airline_staff where username=\'{}\' and password=md5(\'{}\')"
        cursor.execute(query2.format(db_username,password))
        data2=cursor.fetchone()
        cursor.close()
        
        if (data2):
            session['username']=username
            return render_template('staffhome.html',username=username,flights=data1)
        else:
            error='Invalid login or username'
            return render_template('stafflogin.html',error=error)
    else:
        session.clear()
        return render_template('404.html')
        
@app.route('/staffregistercheck',methods=['GET', 'POST'])
def staffregistercheck():
        
    if "password" in request.form and "first_name" in request.form and "last_name" in request.form and "date_of_birth" in request.form and "airline_name" in request.form:
        username = request.form['username']
        password = request.form['password']
        first_name = check_input(request.form['first_name'])
        last_name = check_input(request.form['last_name'])
        date_of_birth = request.form['date_of_birth']
        airline_name = check_input(request.form['airline_name'])
        db_username = check_input(username)
        
        
        cursor=conn.cursor()
        query1="select * from airline_staff where username=\'{}\'"
        cursor.execute(query1.format(db_username))
        data1=cursor.fetchone()
        if (data1):
            error="User already exists. Please change a username"
            return render_template('staffregister.html',error=error)
            
        query2="select airline_name from airline where airline_name=\'{}'"
        cursor.execute(query2.format(airline_name))
        data2=cursor.fetchall()
        error=None
        
        if (data2):
            insertion="insert into airline_staff values(\'{}\', md5(\'{}\'), \'{}\', \'{}\', \'{}\',\'{}\')"
            cursor.execute(insertion.format(db_username,password,first_name,last_name,date_of_birth,airline_name))
            conn.commit()
            query3="SELECT username, airline_name, airplane_id, flight_num, departure_airport, arrival_airport, departure_time, arrival_time FROM flight NATURAL JOIN airline_staff WHERE username = \'{}\' and status = 'upcoming' and datediff(CURDATE(),DATE(departure_time)) < 30 "
            cursor.execute(query3.format(db_username))
            data3=cursor.fetchall()
            cursor.close()
            flash("Logged in!")
            session['username']=username
            return render_template('staffhome.html',username=username,flights=data3)
        else:
            error="Airline does not exist"
            cursor.close()
            return render_template('staffregister.html',error=error)
    else:
        session.clear()
        return render_template('404.html')
        
@app.route('/staffhome')
def staffhome():
    if session.get('username'):
        username = session['username']
        db_username = check_input(username)

        cursor = conn.cursor()
        query = "SELECT username, airline_name, airplane_id, flight_num, departure_airport, arrival_airport, departure_time, arrival_time \
                FROM flight NATURAL JOIN airline_staff \
                WHERE username = \'{}\' and status = 'upcoming' and datediff(CURDATE(), DATE(departure_time)) < 30 and datediff(DATE(departure_time),CURDATE()) > 0"
        cursor.execute(query.format(db_username))
        data1 = cursor.fetchall()
        cursor.close()
        return render_template('staffhome.html', username=username, flights=data1)
    else:
        session.clear()
        return render_template('404.html')
        
@app.route('/staffflight')
def staffflight():
    if session.get('username'):
        username = session['username']
        db_username = check_input(username)
        
        cursor = conn.cursor()
        query = "SELECT username, airline_name FROM airline_staff \
                WHERE username = \'{}\'"
        cursor.execute(query.format(db_username))
        data1 = cursor.fetchall()
        cursor.close()

        return render_template('staffflight.html', username=username, name = data1)
    else:
        session.clear()
        return render_template('404.html')
        
@app.route('/staffsearchflight', methods=['GET', 'POST'])
def staffsearchflight():
    if session.get('username'):
        departure_city = check_input(request.form['departure_city'])
        departure_airport = check_input(request.form['departure_airport'])
        arrival_city = check_input(request.form['arrival_city'])
        arrival_airport = check_input(request.form['arrival_airport'])
        departure_date = request.form['departure_date']
        arrival_date = request.form['arrival_date']
        username = session['username']
        db_username = check_input(username)

        cursor = conn.cursor()
        query = "SELECT airline_name, airplane_id, flight_num, D.airport_city, departure_airport, A.airport_city, arrival_airport, departure_time, arrival_time, status, price\
                FROM airport as D, flight NATURAL JOIN airline_staff, airport AS A \
                WHERE D.airport_city = if (\'{}\' = '',D.airport_city, \'{}\') and \
                        D.airport_name = departure_airport and \
                        departure_airport = if (\'{}\' = '', departure_airport, \'{}\') and \
                        A.airport_city = if (\'{}\' = '', A.airport_city, \'{}\')and \
                        A.airport_name = arrival_airport and \
                        arrival_airport =  if (\'{}\' = '', arrival_airport, \'{}\')and \
                        date(departure_time) = if (\'{}\' = '', date(departure_time), \'{}\')and \
                        date(arrival_time) =  if (\'{}\' = '', date(arrival_time), \'{}\') and \
                        username = \'{}\' \
                ORDER BY airline_name, flight_num"
        cursor.execute(query.format(departure_city, departure_city,departure_airport,departure_airport, arrival_city, arrival_city, arrival_airport, arrival_airport, departure_date, departure_date, arrival_date,arrival_date,db_username))
        data1 = cursor.fetchall()

        query = "SELECT username, airline_name FROM airline_staff \
                WHERE username = \'{}\'"
        cursor.execute(query.format(db_username))
        data2 = cursor.fetchall()

        cursor.close()
        
        if (data1): # has data
            return render_template('staffflight.html', username=username, flights=data1, name = data2)
        else: # does not have data
            error = 'Sorry ... Cannot find this flight!'
            return render_template('staffflight.html', username=username, error1=error, name = data2)
    else:
        session.clear()
        return render_template('404.html')
        
@app.route('/change_status', methods=['GET', 'POST'])
def change_status():
    if session.get('username'):
        username = session['username']
        db_username = check_input(username)
        status = request.form['change_status']
        flight_num = request.form['flight_num']
        
        cursor = conn.cursor()
        upd = "UPDATE flight set status = \'{}\' WHERE flight_num = \'{}\'"
        cursor.execute(upd.format(status, flight_num))
        conn.commit()

        query = "SELECT username, airline_name FROM airline_staff \
                WHERE username = \'{}\'"
        cursor.execute(query.format(db_username))
        data1 = cursor.fetchall()

        cursor.close()
        message = 'Successful!'
        return render_template('staffflight.html', username=username, message = message, name = data1)
    else:
        session.clear()
        return render_template('404.html')
        
@app.route('/staffadd')
def staffadd():
    if session.get('username'):
        username = session['username']
        db_username = check_input(username)
        cursor = conn.cursor()

        query = "SELECT username, airline_name FROM airline_staff \
        WHERE username = \'{}\'"
        cursor.execute(query.format(db_username))
        data1 = cursor.fetchall()

        query = "SELECT airplane_id, seats FROM airplane NATURAL JOIN airline_staff WHERE username = \'{}\'"
        cursor.execute(query.format(db_username))
        data2 = cursor.fetchall()
        
        query = "SELECT flight_num, airplane_id FROM flight NATURAL JOIN airline_staff WHERE username = \'{}\'and status = 'upcoming' and datediff(DATE(departure_time),CURDATE()) < 30 and datediff(DATE(departure_time),CURDATE()) > 0 "
        cursor.execute(query.format(db_username))
        #stores the results in a variable
        data3 = cursor.fetchall()
        cursor.close()

        return render_template('staffadd.html', username=username, airplane = data2, flights=data3, name = data1)
    else:
        session.clear()
        return render_template('404.html')


@app.route('/staffaddflight', methods=['GET', 'POST'])
def staffaddflight():
    if session.get('username'):
        username = session['username']
        db_username = check_input(username)
        # airline_name = check_apostrophe(request.form['airline_name'])
        flight_num = request.form['flight_num']
        departure_airport = check_input(request.form['departure_airport'])
        departure_date = request.form['departure_date']
        departure_time = request.form['departure_time']
        arrival_airport = check_input(request.form['arrival_airport'])
        arrival_date = request.form['arrival_date']
        arrival_time = request.form['arrival_time']
        price = request.form['price']
        number = request.form['number']
        status = request.form['status']
        airplane_id = request.form['airplane_id']

        cursor = conn.cursor()
        query = "SELECT username, airline_name FROM airline_staff \
        WHERE username = \'{}\'"
        cursor.execute(query.format(db_username))
        data2 = cursor.fetchall()

        airline = "SELECT airline_name \
        FROM airline_staff \
        WHERE username = \'{}\'"
        cursor.execute(airline.format(db_username))

        airline_name = cursor.fetchone()
        airline_name = airline_name[0]
        query = "SELECT airport_name FROM airport WHERE airport_name = \'{}\'"
        cursor.execute(query.format(departure_airport))
        #stores the results in a variable
        data = cursor.fetchall()
        
        query = "SELECT airplane_id, seats FROM airplane NATURAL JOIN airline_staff WHERE username = \'{}\'"
        cursor.execute(query.format(db_username))
        data1 = cursor.fetchall()
        
        query = "SELECT flight_num, airplane_id FROM flight NATURAL JOIN airline_staff WHERE username = \'{}\'"
        cursor.execute(query.format(db_username))
        #stores the results in a variable
        data3 = cursor.fetchall()
        error1 = None
        if not (data):
            #If the previous query returns data, then user exists
            error1 = "Departure airport doesn't exist"
#            query = "SELECT airplane_id, seats FROM airplane NATURAL JOIN airline_staff WHERE username = \'{}\'"
#            cursor.execute(query.format(db_username))
#            data1 = cursor.fetchall()
            return render_template('staffadd.html', error1 = error1, username=username, airplane = data1,flights=data3, name = data2)


        query = "SELECT airplane_id FROM airplane WHERE airline_name = \'{}\' and airplane_id = \'{}\'"
        cursor.execute(query.format(airline_name, airplane_id))
        #stores the results in a variable
        data = cursor.fetchall()
        error1 = None
        if not (data):
            #If the previous query returns data, then user exists
            error1 = "Airplane doesn't exist"
            return render_template('staffadd.html', error1 = error1, username=username, airplane = data1,flights=data3, name = data2)
        # cursor.close()
        #executes query
        # cursor = conn.cursor()
        num = "SELECT seats FROM airplane NATURAL JOIN airline_staff WHERE username = \'{}\' and airplane_id = \'{}\'"
        cursor.execute(num.format(db_username, airplane_id))
        num = cursor.fetchone()
        if int(number) > int(num[0]):
            numerror = "Not enough seats"
            return render_template('staffadd.html', error1 = numerror, username=username, airplane = data1,flights=data3, name = data2)

        query = "SELECT airline_name, flight_num FROM flight WHERE airline_name = \'{}\' and flight_num = \'{}\'"
        cursor.execute(query.format(airline_name, flight_num))
        #stores the results in a variable
        data = cursor.fetchone()
        #use fetchall() if you are expecting more than 1 data row
        error1 = None
        
        if(data):
            #If the previous query returns data, then user exists
            error1 = "This flight already exists"
            return render_template('staffadd.html', error1 = error1, username=username, airplane = data1,flights=data3, name = data2)

        else:
            ins = "INSERT INTO flight VALUES(\'{}\', \'{}\', \'{}\', \'{},{}\', \'{}\', \'{},{}\', \'{}\', \'{}\', \'{}\')"
            cursor.execute(ins.format(airline_name, flight_num, departure_airport, departure_date, departure_time, arrival_airport, arrival_date, arrival_time, price, status, airplane_id))
            conn.commit()
            message1 = "New flight added"
            # flash()
            query = "SELECT flight_num, airplane_id FROM flight NATURAL JOIN airline_staff WHERE username = \'{}\'"
            cursor.execute(query.format(db_username))
            #stores the results in a variable
            data3 = cursor.fetchall()
            return render_template('staffadd.html', message1 = message1, username=username, airplane = data1,flights=data3, name = data2)
    else:
        session.clear()
        return render_template('404.html')

@app.route('/staffaddairplane', methods=['GET', 'POST'])
def staffaddairplane():
    if session.get('username'):
        username = session['username']
        db_username = check_input(username)
        
        #grabs information from the forms
        # airline_name = check_apostrophe(request.form['airline_name'])
        airplane_id = request.form['airplane_id']
        seats = request.form['seats']

        #cursor used to send queries
        cursor = conn.cursor()
        query = "SELECT username, airline_name FROM airline_staff \
        WHERE username = \'{}\'"
        cursor.execute(query.format(db_username))
        data2 = cursor.fetchall()

        airline = "SELECT airline_name \
        FROM airline_staff \
        WHERE username = \'{}\'"
        cursor.execute(airline.format(db_username))

        airline_name = cursor.fetchone()
        airline_name = airline_name[0]
        
        query = "SELECT flight_num, airplane_id FROM flight NATURAL JOIN airline_staff WHERE username = \'{}\'"
        cursor.execute(query.format(db_username))
        #stores the results in a variable
        data3 = cursor.fetchall()

        query = "SELECT airline_name, airplane_id FROM airplane WHERE airline_name = \'{}\' and airplane_id = \'{}\'"
        cursor.execute(query.format(airline_name, airplane_id))
        #stores the results in a variable
        data = cursor.fetchone()
        #use fetchall() if you are expecting more than 1 data row
        error2 = None
        if(data):
            #If the previous query returns data, then user exists
            error2 = "This airplane already exists"
            query = "SELECT airplane_id, seats FROM airplane NATURAL JOIN airline_staff WHERE username = \'{}\'"
            cursor.execute(query.format(username))
            data1 = cursor.fetchall()
            cursor.close()
            return render_template('staffadd.html', error2 = error2, username=username, airplane = data1,flights=data3, name = data2)
        else:
            ins = "INSERT INTO airplane VALUES(\'{}\', \'{}\', \'{}\')"
            cursor.execute(ins.format(airline_name, airplane_id, seats))

            query = "SELECT airplane_id, seats FROM airplane NATURAL JOIN airline_staff WHERE username = \'{}\'"
            cursor.execute(query.format(db_username))
            data1 = cursor.fetchall()

            conn.commit()
            cursor.close()
            message2 = "New airplane added"
            # flash()
            return render_template('staffadd.html', message2 = message2, username=username, airplane = data1,flights=data3, name = data2)
    else:
        session.clear()
        return render_template('404.html')

@app.route('/staffaddairport', methods=['GET', 'POST'])
def staffaddairport():
    if session.get('username'):
        username = session['username']
        db_username = check_input(username)
        airport_city = check_input(request.form['airport_city'])
        airport_name=check_input(request.form['airport_name'])

        cursor = conn.cursor()
        query = "SELECT username, airline_name FROM airline_staff \
        WHERE username = \'{}\'"
        cursor.execute(query.format(db_username))
        data2 = cursor.fetchall()

        airport = "SELECT airport_name FROM airport WHERE airport_name = \'{}\'"
        cursor.execute(airport.format(airport_name))
        airportdata = cursor.fetchone()
        query = "SELECT airplane_id, seats FROM airplane NATURAL JOIN airline_staff WHERE username = \'{}\'"
        cursor.execute(query.format(db_username))
        data1 = cursor.fetchall()
        cursor.close()
        error3 = None
        if(airportdata):
            error3 = "This airport already exists"
            return render_template('staffadd.html', error3 = error3, username=username, airplane = data1, posts = data2)

        else:
            cursor = conn.cursor()
            ins = "INSERT INTO airport VALUES(\'{}\', \'{}\')"
            cursor.execute(ins.format(airport_name, airport_city))
            conn.commit()
            cursor.close()
            message3 = "New airport added"
            return render_template('staffadd.html', message3 = message3, username=username, airplane = data1, posts = data2)
    else:
        session.clear()
        return render_template('404.html')
            
@app.route('/staffagent')
def staffagent():
    if session.get('username'):
        username = session['username']
        db_username = check_input(username)
        # airline_name = session['airline_name']
        cursor = conn.cursor()

        query = "SELECT username, airline_name FROM airline_staff \
        WHERE username = \'{}\'"
        cursor.execute(query.format(db_username))
        data = cursor.fetchall()

        query1 = "SELECT email, booking_agent_id, sum(price) * 0.1 as total FROM booking_agent NATURAL JOIN purchases \
            NATURAL JOIN flight NATURAL JOIN ticket AS T, airline_staff \
            WHERE username = \'{}\' and airline_staff.airline_name = T.airline_name and datediff(CURDATE(), DATE(purchase_date)) < 365  \
                GROUP BY email, booking_agent_id \
                    ORDER BY total DESC\
                        LIMIT 5 "
        cursor.execute(query1.format(db_username))
        commission= cursor.fetchall()

        query2 = "SELECT booking_agent.email, booking_agent_id, count(ticket_id) as ticket FROM booking_agent NATURAL JOIN purchases \
            NATURAL JOIN ticket AS T, airline_staff \
            WHERE username = \'{}\' and airline_staff.airline_name = T.airline_name and datediff(CURDATE(), DATE(purchase_date)) < 30 \
                GROUP BY email, booking_agent_id \
                    ORDER BY ticket DESC LIMIT 5 "
        cursor.execute(query2.format(db_username))
        monthlytickets = cursor.fetchall()

        query3 = "SELECT email, booking_agent_id, count(ticket_id) as ticket FROM booking_agent NATURAL JOIN purchases \
            NATURAL JOIN ticket AS T, airline_staff \
            WHERE username = \'{}\' and airline_staff.airline_name = T.airline_name and datediff(CURDATE(), DATE(purchase_date)) < 365 \
                GROUP BY email, booking_agent_id \
                    ORDER BY ticket DESC LIMIT 5 "
        cursor.execute(query3.format(db_username))
        yearlytickets = cursor.fetchall()

        query = "SELECT email, booking_agent_id FROM booking_agent"
        cursor.execute(query)
        name = cursor.fetchall()
        cursor.close()
        return render_template('staffagent.html', username=username, commission = commission, month = monthlytickets, year = yearlytickets, name = name, data = data)
    else:
        session.clear()
        return render_template('404.html')
        
@app.route('/staffcustomer')
def staffcustomer():
    if session.get('username'):
        username = session['username']
        db_username = check_input(username)
        # airline_name = session['airline_name']
        cursor = conn.cursor()
        query = "SELECT username, airline_name FROM airline_staff \
        WHERE username = \'{}\'"
        cursor.execute(query.format(db_username))
        name = cursor.fetchall()

        query1 = "SELECT email, name, count(ticket_id) as ticket FROM customer, purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN airline_staff \
            WHERE email = customer_email AND username = \'{}\' and datediff(CURDATE(), DATE(purchase_date)) < 365\
            GROUP BY email, name\
            ORDER BY ticket DESC LIMIT 1"
        cursor.execute(query1.format(db_username))
        # cursor.execute(query1)
        customers = cursor.fetchall()
        cursor.close()
        return render_template('staffcustomer.html', customers = customers, username = username, name = name)
    else:
        session.clear()
        return render_template('404.html')

@app.route('/staffcustomerflight', methods=['GET', 'POST'])
def staffcustomerflight():
    if session.get('username'):
        username = session['username']
        db_username = check_input(username)
        email = request.form['customer_email']
        db_email = check_input(email)

        cursor = conn.cursor()
        query = "SELECT username, airline_name FROM airline_staff \
        WHERE username = \'{}\'"
        cursor.execute(query.format(db_username))
        name = cursor.fetchall()

        query2 = "SELECT DISTINCT airplane_id, flight_num, \
            departure_airport, arrival_airport, departure_time, arrival_time, \
                status FROM customer, \
                    purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN airline_staff\
            WHERE email = \'{}\' and email = customer_email and username = \'{}\'"
        cursor.execute(query2.format(db_email, db_username))
        # cursor.execute(query2)
        flights = cursor.fetchall()

        query1 = "SELECT email, name, count(ticket_id) as ticket FROM customer, purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN airline_staff \
            WHERE email = customer_email AND username = \'{}\' and datediff(CURDATE(), DATE(purchase_date)) < 365\
            GROUP BY email, name\
            ORDER BY ticket DESC LIMIT 1"
        cursor.execute(query1.format(db_username))
        # cursor.execute(query1)
        customers = cursor.fetchall()
        cursor.close()

        error = None
        if(flights):
            return render_template('staffcustomer.html', flights = flights, customers = customers, username = username, name = name)
        else:
            cursor = conn.cursor()
            cus = "SELECT email FROM customer WHERE email = \'{}\'"
            cursor.execute(cus.format(db_email))
            # cursor.execute(query2)
            cus = cursor.fetchone()
            cursor.close()
            if(cus):
                error = "No Flight taken by this customer"
            # cursor.close()
            else:
                error = "Invalid Customer. Please try again!"
            return render_template('staffcustomer.html', error = error, customers = customers, username = username, name = name)
    else:
        session.clear()
        return render_template('404.html')
        
@app.route('/staffDest')
def staffDest():
    if session.get('username'):
        username = session['username']
        db_username = check_input(username)
        cursor = conn.cursor()
        
        query1 = "SELECT airport_city, count(ticket_id) AS ticket FROM \
            purchases NATURAL JOIN ticket NATURAL JOIN flight, airport \
            WHERE airport_name = arrival_airport and datediff(CURDATE(), DATE(purchase_date)) < 90\
            GROUP BY airport_city\
            ORDER BY ticket DESC\
                LIMIT 3"
        cursor.execute(query1)
        monthly = cursor.fetchall()

        query2 = "SELECT airport_city, count(ticket_id) AS ticket FROM \
            purchases NATURAL JOIN ticket NATURAL JOIN flight, airport \
            WHERE airport_name = arrival_airport and datediff(CURDATE(), DATE(purchase_date)) < 365\
                GROUP BY airport_city\
            ORDER BY ticket DESC\
                LIMIT 3"
        cursor.execute(query2)
        # cursor.execute(query1)
        yearly = cursor.fetchall()
        cursor.close()
        return render_template('staffDest.html', monthly = monthly, yearly = yearly, username = username)

    else:
        session.clear()
        return render_template('404.html')
            
@app.route('/staffReve')
def staffReve():
    if session.get('username'):
        username = session['username']
        db_username = check_input(username)

        cursor = conn.cursor()
        
        query = "SELECT username, airline_name FROM airline_staff \
        WHERE username = \'{}\'"
        cursor.execute(query.format(db_username))
        data2 = cursor.fetchall()

        query3 = "SELECT sum(price)\
        FROM purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN airline_staff\
        WHERE username = \'{}\' AND booking_agent_id is NULL AND datediff(CURDATE(), DATE(purchase_date)) < 30\
        GROUP BY airline_name"

        cursor.execute(query3.format(db_username))
        # cursor.execute(query1)
        mdirect = cursor.fetchall()
        if(mdirect):
            mdirect = [int(mdirect[0][0])]
        else:
            mdirect = [0]

        query4 = "SELECT sum(price)\
        FROM purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN airline_staff\
        WHERE username = \'{}\' AND booking_agent_id is NOT NULL AND datediff(CURDATE(), DATE(purchase_date)) < 30\
        GROUP BY airline_name"
        
        cursor.execute(query4.format(db_username))
        # cursor.execute(query1)
        mindirect = cursor.fetchall()
        if(mindirect):
            mindirect = [int(mindirect[0][0])]
        else:
            mindirect = [0]

        query5 = "SELECT sum(price)\
        FROM purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN airline_staff\
        WHERE username = \'{}\' AND booking_agent_id is NULL AND datediff(CURDATE(), DATE(purchase_date)) < 365\
        GROUP BY airline_name"
        
        cursor.execute(query5.format(db_username))
        # cursor.execute(query1)
        ydirect = cursor.fetchall()
        if(ydirect):
            ydirect = [int(ydirect[0][0])]
        else:
            ydirect = [0]

        query6 = "SELECT sum(price)\
        FROM purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN airline_staff\
        WHERE username = \'{}\' AND booking_agent_id is NOT NULL AND datediff(CURDATE(), DATE(purchase_date)) < 365\
        GROUP BY airline_name"
        
        cursor.execute(query6.format(db_username))
        # cursor.execute(query1)
        yindirect = cursor.fetchall()
        if(yindirect):
            yindirect = [int(yindirect[0][0])]
        else:
            yindirect = [0]
        
        cursor.close()
        return render_template('staffReve.html', username = username, mdirect = mdirect, mindirect = mindirect, ydirect = ydirect, yindirect = yindirect, name = data2)
    else:
        session.clear()
        return render_template('404.html')

@app.route('/staffTickets')
def staffTickets():
    if session.get('username'):
        username = session['username']
        db_username = check_input(username)

        cursor = conn.cursor()
        query = "SELECT username, airline_name FROM airline_staff \
        WHERE username = \'{}\'"
        cursor.execute(query.format(db_username))
        data2 = cursor.fetchall()
        cursor.close()
        
        return render_template('staffTickets.html', username = username, posts = data2)
    else:
        session.clear()
        return render_template('404.html')

@app.route('/stafffixticket', methods=['GET', 'POST'])
def stafffixticket():
    if session.get('username'):
        username = session['username']
        db_username = check_input(username)
        duration = request.form.get("duration")
        fallticket = None
        
        cursor = conn.cursor()
        query = "SELECT username, airline_name FROM airline_staff \
        WHERE username = \'{}\'"
        cursor.execute(query.format(db_username))
        data2 = cursor.fetchall()
        
        if duration == 'tmonth':
            ticket = "SELECT YEAR(purchase_date) AS year, MONTH(purchase_date) AS month, count(ticket_id) FROM \
                    purchases NATURAL JOIN airline_staff NATURAL JOIN flight NATURAL JOIN ticket\
                    WHERE datediff(CURDATE(), DATE(purchase_date)) < 30 AND username = \'{}\' \
                    GROUP BY year, month\
                    ORDER BY year, month"

            cursor.execute(ticket.format(db_username))
            # cursor.execute(query1)
            fallticket = cursor.fetchall()
        elif duration == 'tyear':
            ticket = "SELECT YEAR(purchase_date) AS year, MONTH(purchase_date) AS month, count(ticket_id) FROM \
                    purchases NATURAL JOIN airline_staff NATURAL JOIN flight NATURAL JOIN ticket\
                    WHERE datediff(CURDATE(), DATE(purchase_date)) < 365 AND username = \'{}\' \
                    GROUP BY year, month\
                        ORDER BY year, month"

            cursor.execute(ticket.format(db_username))
            fallticket = cursor.fetchall()
        cursor.close()


        if(fallticket):
            fs = str(fallticket[0][0]) + '-' + str(fallticket[0][1])
            fe = str(fallticket[len(fallticket) - 1][0]) + '-' + str(fallticket[len(fallticket) - 1][1])
            ftime = [str(fallticket[i][0]) + '-' + str(fallticket[i][1]) for i in range(len(fallticket))]
            fmonthticket = [fallticket[i][2] for i in range(len(fallticket))]
            ftotal = sum(fmonthticket)

            return render_template('staffTickets.html', fs = fs, fe = fe, ft = ftotal, ftime = ftime, fmonthticket = fmonthticket, fticket = fallticket, username = username, posts = data2)
        else:
            ferror = "No ticket sold!"
            return render_template('staffTickets.html', ferror = ferror, username = username, posts = data2)
    else:
        session.clear()
        return render_template('404.html')

@app.route('/staffticket', methods=['GET', 'POST'])
def staffticket():
    if session.get('username'):
        username = session['username']
        db_username = check_input(username)
        # duration = request.form.get("duration")
        start = request.form['start']
        end = request.form['end']
        cursor = conn.cursor()
        query = "SELECT username, airline_name FROM airline_staff \
        WHERE username = \'{}\'"
        cursor.execute(query.format(db_username))
        data2 = cursor.fetchall()

        ticket = "SELECT YEAR(purchase_date) AS year, MONTH(purchase_date) AS month, count(ticket_id) FROM \
                purchases NATURAL JOIN airline_staff NATURAL JOIN flight NATURAL JOIN ticket\
                WHERE purchase_date > \'{}\'\
                and purchase_date < \'{}\' AND username = \'{}\' \
                GROUP BY year, month\
                    ORDER BY year, month"
        cursor.execute(ticket.format(start, end, db_username))
        allticket = cursor.fetchall()
        cursor.close()


        if(allticket):
            s = str(allticket[0][0]) + '-' + str(allticket[0][1])
            e = str(allticket[len(allticket) - 1][0]) + '-' + str(allticket[len(allticket) - 1][1])
            time = [str(allticket[i][0]) + '-' + str(allticket[i][1]) for i in range(len(allticket))]
            monthticket = [allticket[i][2] for i in range(len(allticket))]
            total = sum(monthticket)

            return render_template('staffTickets.html', s = s, e = e, t = total, time = time, monthticket = monthticket, ticket = allticket, username = username, posts = data2)
        else:
            error = "No ticket sold"
            return render_template('staffTickets.html', error = error, username = username, posts = data2)
    else:
        session.clear()
        return render_template('404.html')
        
        
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/customerlogin')



app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
