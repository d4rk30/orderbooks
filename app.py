import os
import sys
import click

from flask import Flask,render_template,flash,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import DataRequired,Length

WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
app.secret_key = 'your_secret_key_here'
# 在扩展类实例化前加载配置
db = SQLAlchemy(app)
bootstrap = Bootstrap5(app)

##DB Design

#xxzXZXZXzXzXZXzZXzXZXzX
class Commodity(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    number = db.Column(db.Interger,unique=False,nullabel=False)
    type = db.Column(db.String,nullabel=False)
    price = db.Column(db.Float,nullabel=False)
    description = db.Column(db.Text)
    
    images = db.relationship('Images',back_populates = 'commodity')

class Image(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    path = db.Column(db.Text)
    
    commodity_id = db.Column(db.Integer,db.ForeignKey('commodity.id'))
    commodity = db.relationship('Commodity',back_populates = 'images')

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_wechat = db.Column(db.Text)
    phone = db.Column(db.Integer)

    orders
    consignees

class Order(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    number = db.Column(db.Interger,unique=False,nullabel=False)

class Consignee(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    address = db.Column(db.Text)
    phone = db.Column(db.Integer)
    name = db.Column(db.String,nullabel=False)
    
    expressage_id = db.Column(db.Integer,nullabel=False)

class Expressage(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    phone = db.Column(db.Integer)
    license_number = db.Column(db.String,nullabel=False)

@app.route('/')
def index():
    form = LForm()
    return render_template('index.html',form=form)

@app.route('/')
def explore():
    return render_template('index.html')

@app.route('/')
def about():
    return render_template('index.html')





@app.cli.command()  # 注册为命令，可以传入 name 参数来自定义命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # 输出提示信息

@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(e):  # 接受异常对象作为参数
    user = User.query.first()
    return render_template('404.html', user=user), 404  # 返回模板和状态码

@app.route('/flash')
def just_flash():
    flash('的消息存储在session中?')
    return redirect(url_for('index'))