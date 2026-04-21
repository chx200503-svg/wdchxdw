from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view= 'login'

# 用户模型
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))

# 图片模型
class Artwork(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))
    user_id = db.Column(db.Integer)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 首页
@app.route('/')
def index():
    artworks = Artwork.query.all()
    return render_template('index.html', artworks=artworks)

# 登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect('/')
    return render_template('login.html')

# 上传
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            art = Artwork(filename=file.filename, user_id=current_user.id)
            db.session.add(art)
            db.session.commit()

            return redirect('/')
    return render_template('upload.html')
import uuid
filename = str(uuid.uuid4()) + ".jpg"

# 登出
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

if __name__ == '__main__':
    with app.app_context():
      if not User.query.filter_by(username="test").first():
        user = User(username="test", password="123456")
        db.session.add(user)
        db.session.commit()
    
@app.route('/delete/<int:id>')
@login_required
def delete(id):
    art = Artwork.query.get_or_404(id)

    # ❗防止删别人作品（重要）
    if art.user_id != current_user.id:
        return "无权限删除"

    # 删除图片文件
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], art.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    # 删除数据库记录
    db.session.delete(art)
    db.session.commit()

    return redirect('/')

app.run()