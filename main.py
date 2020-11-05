from flask import Flask, render_template, session, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import json
import math
import os

params, error, edit, isBusy, gotBooked, sent, clientError, done = None, False, False, None, None, None, None, None
with open('config.json') as file:
    params = json.load(file)

app = Flask(__name__)
app.secret_key = 'my-secret-super-key'

if params['database']['isLocal']:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['database']['localURI']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['database']['prodURI']


db = SQLAlchemy(app)
app.config['UPLOAD_FOLDER'] = params['webData']['projectUpload']
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['social']['mailAddr'],
    MAIL_PASSWORD=params['social']['mailPass']
)
mailApp = Mail(app)


class Service(db.Model):
    __tablename__ = 'service'

    def __init__(self, title, desc, slug, icon, price, det1, det2, det3, det4, det5):
        self.serviceTitle = title
        self.serviceDesc = desc
        self.slug = slug
        self.serviceIcon = icon
        self.fees = price
        self.serviceDetails1 = det1
        self.serviceDetails2 = det2
        self.serviceDetails3 = det3
        self.serviceDetails4 = det4
        self.serviceDetails5 = det5

    serviceID = db.Column('service_id', db.Integer, primary_key=True)
    serviceTitle = db.Column('title', db.String(100), nullable=False)
    serviceDesc = db.Column('service_desc', db.String(500), nullable=False)
    slug = db.Column('slug', db.String(100), nullable=False)
    serviceIcon = db.Column('service_icon', db.String(100), nullable=False)
    fees = db.Column('fees', db.Integer, nullable=False)
    serviceDetails1 = db.Column('detail1', db.String(500), nullable=False)
    serviceDetails2 = db.Column('detail2', db.String(500), nullable=False)
    serviceDetails3 = db.Column('detail3', db.String(500), nullable=False)
    serviceDetails4 = db.Column('detail4', db.String(500), nullable=False)
    serviceDetails5 = db.Column('detail5', db.String(500), nullable=False)


class Pictures(db.Model):
    __tablename__ = 'pictures'

    def __init__(self, id, genre, service, loc, caption, name, rating):
        self.clientID = id
        self.picGenre = genre
        self.picService = service
        self.picLocation = loc
        self.picCaption = caption
        self.picName = name
        self.picRating = rating

    picID = db.Column('pic_id', db.Integer, primary_key=True)
    clientID = db.Column('client_id', db.Integer, nullable=False)
    picName = db.Column('pic_name', db.String(1000), nullable=False)
    picGenre = db.Column('pic_genre', db.String(100), nullable=False)
    picService = db.Column('pic_service', db.String(100), nullable=False)
    picLocation = db.Column('location', db.String(100), nullable=False)
    picCaption = db.Column('pic_caption', db.String(100), nullable=False)
    picRating = db.Column('rating', db.Integer, nullable=False)


class Clients(db.Model):
    __tablename__ = 'clients'

    def __init__(self, name, mail, date, addr, city, state, zip, contact, logid, passwd):
        self.clientName = name
        self.clientMail = mail
        self.clientDate = date
        self.clientAddr = addr
        self.clienCity = city
        self.clientState = state
        self.clientZIP = zip
        self.clientContact = contact
        self.clientLogID = logid
        self.clientPasswd = passwd

    clientID = db.Column('id', db.Integer, primary_key=True)
    clientName = db.Column('name', db.String(1000), nullable=False)
    clientMail = db.Column('email', db.String(100), nullable=False)
    clientDate = db.Column('date', db.String(100), nullable=False)
    clientAddr = db.Column('address', db.String(200), nullable=False)
    clienCity = db.Column('city', db.String(100), nullable=False)
    clientState = db.Column('state', db.String(100), nullable=False)
    clientZIP = db.Column('zip', db.String(100), nullable=False)
    clientContact = db.Column('contact', db.Integer, nullable=False)
    clientLogID = db.Column('loginid', db.Integer, nullable=False)
    clientPasswd = db.Column('password', db.String(100), nullable=False)
    clientFeedback = db.Column('feedback', db.String(1000), nullable=True)


class Bookings(db.Model):
    __tablename__ = 'bookings'

    def __init__(self, clientid, serviceid):
        self.clientID = clientid
        self.serviceID = serviceid

    bookingID = db.Column('bookingid', db.Integer, primary_key=True)
    clientID = db.Column('clientid', db.Integer, nullable=False)
    serviceID = db.Column('serviceid', db.Integer, nullable=False)


class Messages(db.Model):
    __tablename__ = 'messages'

    def __init__(self, name, mail, subject, client, msg):
        self.name = name
        self.email = mail
        self.subject = subject
        self.clientID = client
        self.message = msg

    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String(100), nullable=False)
    email = db.Column('email', db.String(100), nullable=False)
    subject = db.Column('subject', db.String(100), nullable=False)
    clientID = db.Column('clientid', db.Integer, nullable=False)
    message = db.Column('message', db.String(5000), nullable=False)


def getReviewDetails():
    reviewPics = Pictures.query.order_by(Pictures.picRating).all()
    reviewPart = list()
    count = 0
    for pic in reviewPics:
        if pic.clientID != 0:
            entry = Clients.query.filter_by(clientLogID=pic.clientID).first()
            name = entry.clientName
            review = entry.clientFeedback
            rating = pic.picRating
            picName = pic.picName
            reviewPart.append([picName, name, rating, review])
            count += 1
            if count == 3:
                break
    return reviewPart


def isLoggedIn():
    if 'client' in session:
        return True
    else:
        return False


@app.route('/')
def home():
    servicesObj = Service.query.all()
    pics = Pictures.query.all()
    genres = []
    for pic in pics:
        if pic.picGenre not in genres and pic.picName is not None:
            genres.append(pic.picGenre)
    return render_template('index.html', params=params, servicesObj=servicesObj, pics=pics, genres=genres, reviewPart=getReviewDetails(), isLoggedIn=isLoggedIn())


@app.route('/about')
def about():
    return render_template('about-us.html', params=params, isLoggedIn=isLoggedIn())


@app.route('/show/<string:id>')
def showMessage(id):
    if 'user' in session:
        message = Messages.query.filter_by(id=id).first()
        return render_template('showMessage.html', params=params, message=message)
    else:
        return '404 - Not Found'


@app.route('/delMessage/<string:id>')
def delMessage(id):
    if 'user' in session:
        message = Messages.query.filter_by(id=id).first()
        db.session.delete(message)
        db.session.commit()
        return redirect('/manage#messages')
    else:
        return '404 - Not Found'


@app.route('/service')
def service():
    servicesObj = Service.query.all()
    return render_template('service.html', params=params, servicesObj=servicesObj, reviewPart=getReviewDetails(), isLoggedIn=isLoggedIn())


@app.route('/project')
def project():
    pics = Pictures.query.all()
    genres = []
    for pic in pics:
        if pic.picGenre not in genres and pic.picName is not None:
            genres.append(pic.picGenre)
    return render_template('project.html', params=params, genres=genres, pics=pics, reviewPart=getReviewDetails(), isLoggedIn=isLoggedIn())


@app.route('/contact', methods=['POST', 'GET'])
def contact():
    global sent
    if 'client' in session:
        if request.method == 'GET':
            client = Clients.query.filter_by(clientLogID=session['client']).first()
            if sent is None:
                return render_template('contact.html', params=params, isLoggedIn=isLoggedIn(), client=client,
                                       sent=True, hide=True)
            if sent:
                sent = None
                return render_template('contact.html', params=params, isLoggedIn=isLoggedIn(), client=client,
                                       sent=True)
            else:
                return render_template('contact.html', params=params, isLoggedIn=isLoggedIn(), client=client, sent=False)
        elif request.method == 'POST':
            message = request.form.get('message')
            name = request.form.get('name')
            email = request.form.get('email')
            subject = request.form.get('subject')
            mailApp.send_message(subject + ' From ' + name, sender=email, recipients=[params['social']['mailAddr']],
                              body=message)
            client = Clients.query.filter_by(clientLogID=session['client']).first()
            sent = True
            entry = Messages(name, email, subject, client.clientLogID, message)
            db.session.add(entry)
            db.session.commit()
            return redirect('/contact')
    else:
        if request.method == 'GET':
            if sent is None:
                return render_template('contact.html', params=params, isLoggedIn=isLoggedIn(),
                                       sent=True, hide=True)
            if sent:
                sent = None
                return render_template('contact.html', params=params, isLoggedIn=isLoggedIn(),
                                       sent=True)
            else:
                return render_template('contact.html', params=params, isLoggedIn=isLoggedIn(),
                                       sent=False)
        else:
            message = request.form.get('message')
            name = request.form.get('name')
            email = request.form.get('email')
            subject = request.form.get('subject')
            mailApp.send_message(subject + ' From ' + name, sender=email, recipients=[params['social']['mailAddr']],
                              body=message)
            sent = True
            entry = Messages(name, email, subject, 0, message)
            db.session.add(entry)
            db.session.commit()
            return redirect('/contact')


@app.route('/logout/<string:user>')
def logout(user):
    if user == 'client':
        session.pop('client')
    elif user == 'admin':
        error = False
        session.pop('user')
    return redirect('/')


@app.route('/rateus', methods=['POST', 'GET'])
def rateus():
    global clientError, done
    if 'client' in session:
        if request.method == 'GET':
            pics = Pictures.query.filter_by(clientID=session['client'])
            for pic in pics:
                if pic.picRating > 0:
                    return render_template('rateus.html', params=params, pics=pics, done=True, isLoggedIn=isLoggedIn())

                else:
                    return render_template('rateus.html', params=params, pics=pics, done=False, isLoggedIn=isLoggedIn())
        else:
            rating = request.form.get('rating')
            review = request.form.get('review')
            pics = Pictures.query.filter_by(clientID=session['client'])
            client = Clients.query.filter_by(clientLogID=session['client']).first()
            for pic in pics:
                pic.picRating = math.ceil(int(rating)/25) + 1
            client.clientFeedback = review
            objs = Bookings.query.filter_by(clientID=client.clientLogID)
            for obj in objs:
                db.session.delete(obj)
            db.session.commit()
            done = True
            return redirect('/rateus')
    else:
        if request.method == 'GET':
            if clientError:
                clientError = False
                return render_template('clientLogin.html', params=params, isLoggedIn=isLoggedIn(), error=True)
            else:
                return render_template('clientLogin.html', params=params, isLoggedIn=isLoggedIn(), error=clientError)
        else:
            loginID = request.form.get('logid')
            passwd = request.form.get('password')
            entry = Clients.query.filter_by(clientLogID=loginID).first()
            if entry is not None:
                if entry.clientPasswd == passwd:
                    session['client'] = entry.clientLogID
                    return redirect('/rateus')
                else:
                    clientError = True
                    return redirect('/rateus')
            else:
                clientError = True
                return redirect('/rateus')


@app.route('/bookService/<string:slug>', methods=['POST', 'GET'])
def bookService(slug):
    global isBusy, mail
    obj = Service.query.filter_by(slug=slug).first()
    if request.method == 'GET' and slug == 'done':
        return render_template('booking.html', data=obj, params=params, done=True, isLoggedIn=isLoggedIn())
    elif request.method == 'GET' and slug != 'new':
        if 'client' in session:
            client = Clients.query.filter_by(clientLogID=session['client']).first()
            return render_template('booking.html', data=obj, params=params, isBusy=isBusy, isLoggedIn=isLoggedIn(), client=client, fill=True)
        else:
            return render_template('booking.html', data=obj, params=params, isBusy=isBusy, isLoggedIn=isLoggedIn())
    elif request.method == 'POST' and slug == 'new':
        eventdate = request.form.get('date')
        clientCount = Clients.query.count()
        serviceSlug = request.form.get('slug')
        if Clients.query.filter_by(clientDate=eventdate).count() == 0:
            name = request.form.get('name')
            mail = request.form.get('email')
            addr = request.form.get('address')
            city = request.form.get('city')
            state = request.form.get('state')
            zip = request.form.get('zip')
            contact = request.form.get('contact')
            loginid = int(params['database']['id']) + (4*clientCount) - 1 + int(zip)
            passwd = name.split(' ')[0] + str(loginid // int(zip))
            entry = Clients(name, mail, eventdate, addr, city, state, zip, contact, loginid, passwd)
            serve = Service.query.filter_by(slug=serviceSlug).first()
            anotherOne = Bookings(loginid, serve.serviceID)
            db.session.add(entry)
            db.session.add(anotherOne)
            db.session.commit()
            mailApp.send_message('Booking Confirmation from ' + params['webData']['title'], sender=params['contact-info']['mail'], recipients=[mail],
                              body='Your Booking is Confirmed!')
            return redirect('/bookService/done')
        else:
            isBusy = True
            return redirect('/bookService/'+serviceSlug)
    elif request.method == 'POST' and slug == 'olduser':
        eventdate = request.form.get('date')
        loginid = request.form.get('clientLogID')
        serviceSlug = request.form.get('slug')
        client = Clients.query.filter_by(clientLogID=session['client']).first()
        if Clients.query.filter_by(clientDate=eventdate).count() == 0:
            serve = Service.query.filter_by(slug=serviceSlug).first()
            anotherOne = Bookings(loginid, serve.serviceID)
            db.session.add(anotherOne)
            db.session.commit()
            mailApp.send_message('Booking Confirmation from ' + params['webData']['title'], sender=params['contact-info']['mail'], recipients=[client.clientMail], body='Your Booking is Confirmed!')
            return redirect('/bookService/done')
        else:
            isBusy = True
            return redirect('/bookService/' + serviceSlug)


@app.route('/upload', methods=['POST'])
def upload():
    if 'user' in session:
        imgFile = request.files['imgFile']
        imgFile.save(os.path.join(app.config['UPLOAD_FOLDER'], imgFile.filename))
        clientID = 0
        askUser = request.form.get('askfor')
        if askUser == 'Yes':
            clientID = request.form.get('client_id')
            client = Clients.query.filter_by(clientLogID=clientID).first()
            mailApp.send_message('Pictures Uploaded at ' + params['webData']['title'],
                                 sender=params['contact-info']['mail'], recipients=[client.clientMail],
                                 body='Your Pictures and Videos are Uploaded at ' + params['webData']['title'] + '. <br> Log-in ID : ' + str(client.clientLogID) + '<br> Password : ' + str(client.clientPasswd) + '<br> Please Review Us @ <a href="http://127.0.0.1:5000/rateus" target="_blank"> Pentax Photography </a>')
        genre = request.form.get('genre')
        service_type = request.form.get('service')
        loc = request.form.get('location')
        caption = request.form.get('caption')
        entry = Pictures(clientID, genre, service_type, loc, caption, imgFile.filename, 0)
        db.session.add(entry)
        db.session.commit()
        return redirect('/manage')


@app.route('/service-desc/<string:slug>')
def service_desc(slug):
    obj = Service.query.filter_by(slug=slug).first()
    pics = Pictures.query.filter_by(picService=obj.serviceTitle)
    return render_template('service-desc.html', params=params, data=obj, pics=pics, isLoggedIn=isLoggedIn())


@app.route('/addService/<string:action>/<int:id>', methods=['POST', 'GET'])
def addservice(action, id):
    if action == 'new':
        edit = False
        return render_template('serviceManage.html', params=params, edit=edit)
    elif action == 'delete':
        obj = Service.query.filter_by(serviceID=id).first()
        db.session.delete(obj)
        db.session.commit()
        return redirect('/manage')
    elif action == 'edit':
        edit = True
        obj = Service.query.filter_by(serviceID=id).first()
        return render_template('serviceManage.html', params=params,
                               edit=edit, data=obj)
    elif action == 'save':
        if id == 0:
            title = request.form.get('title')
            desc = request.form.get('desc')
            slug = request.form.get('slug')
            icon = request.form.get('icon')
            price = request.form.get('price')
            det1 = request.form.get('detail1')
            det2 = request.form.get('detail2')
            det3 = request.form.get('detail3')
            det4 = request.form.get('detail4')
            det5 = request.form.get('detail5')
            entry = Service(title, desc, slug, icon, price, det1, det2, det3, det4, det5)
            db.session.add(entry)
            db.session.commit()
        else:
            obj = Service.query.filter_by(serviceID=id).first()
            obj.serviceTitle = request.form.get('title')
            obj.serviceDesc = request.form.get('desc')
            obj.slug = request.form.get('slug')
            obj.serviceIcon = request.form.get('icon')
            obj.fees = request.form.get('price')
            obj.serviceDetails1 = request.form.get('detail1')
            obj.serviceDetails2 = request.form.get('detail2')
            obj.serviceDetails3 = request.form.get('detail3')
            obj.serviceDetails4 = request.form.get('detail4')
            obj.serviceDetails5 = request.form.get('detail5')
            db.session.commit()
        return redirect('/manage')


@app.route('/manage', methods=['GET', 'POST'])
def manage():
    global error
    if request.method == 'GET':
        if 'user' in session:
            servicesObj = Service.query.all()
            clients = []
            bookings = Bookings.query.all()
            messages = Messages.query.all()
            for booking in bookings:
                clients.append(Clients.query.filter_by(clientLogID=booking.clientID).first())
            return render_template('manage.html', params=params, servicesObj=servicesObj, clients=clients, messages=messages)
        else:
            return render_template('login.html', error=error, params=params)
    else:
        mailid = request.form.get('email')
        password = request.form.get('password')
        if mailid == params['superUser']['email'] and password == params['superUser']['password']:
            session['user'] = mailid
            error = False
            servicesObj = Service.query.all()
            clients = []
            bookings = Bookings.query.all()
            for booking in bookings:
                clients.append(Clients.query.filter_by(clientLogID=booking.clientID).first())
            return redirect('/manage')
        else:
            error = True
            return redirect('/manage')


app.run(debug=True)
