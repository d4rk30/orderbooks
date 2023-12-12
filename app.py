import os
import sys
import click

from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from faker import Faker

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


# DB设计
# ---------------------------------------------------------------------------------------
# 货物数据结构
class Commodity(db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True,unique=True)
    # 货号
    number = db.Column(db.Integer,nullable=False)
    # 商品名称
    title = db.Column(db.String(80),nullable=False)
    # 商品描述
    description = db.Column(db.Text)
    # 主图
    main_image = db.Column(db.Text)
    # 商品照片
    images = db.Column(db.JSON)
    # 型号和价格组，每个货物有不同的型号和售价
    models = db.relationship('ModelPrice')

class ModelPrice(db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True,unique=True)
    # 型号
    type = db.Column(db.String,nullable=False)
    # 价格
    price = db.Column(db.Float,nullable=False)
    # 外键-所属的货物
    commodity_id =  db.Column(db.Integer,db.ForeignKey('commodity.id'))

# 用户信息，需要对接微信openID
class User(db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True,unique=True)
    user_wechat = db.Column(db.Text)
    phone = db.Column(db.Integer)

    # 每个用户有自己的订单信息
    orders =  db.relationship('Order')
    # 每个用户有自己的地址信息
    consignees =  db.relationship('Consignee')

# 订单信息
class Order(db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True,unique=True)
    # 订单号
    number = db.Column(db.Integer,nullable=False)
    # 货号
    commodity_number = db.Column(db.Integer,nullable=False)
    # 型号
    type = db.Column(db.String,nullable=False)
    # 数量
    conut = db.Column(db.Integer,nullable=False)
    # 地址
    address = db.Column(db.Text,nullable=False)
    # 手机
    phone = db.Column(db.Integer,nullable=False)
    # 关联的物流车
    expressage_id = db.Column(db.Integer,nullable=False)
    # 收件人
    name = db.Column(db.String,nullable=False)
    # 外键-所属的用户
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))


# 收获地址信息
class Consignee(db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True,unique=True)
    # 地址
    address = db.Column(db.Text,nullable=False)
    # 手机
    phone = db.Column(db.Integer,nullable=False)
    # 收件人
    name = db.Column(db.String,nullable=False)
    # 地址关联的物流车
    expressage_id = db.Column(db.Integer,nullable=False)
    # 外键-所属的用户
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))

# 物流车信息
class Expressage(db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True,unique=True)
    # 物流名字
    title = db.Column(db.String(80),nullable=False)
    # 介绍
    description = db.Column(db.Text)
    # 联系人
    name = db.Column(db.String(80),nullable=False)
    # 手机
    phone = db.Column(db.Integer,nullable=False)
    # 车牌号
    license_number = db.Column(db.String,nullable=False)

# API
# ---------------------------------------------------------------------------------------
@app.route('/api/commoditys')
def get_commoditys():
    page = request.args.get('page', 1, type=int)         # 页数，默认为第1页
    per_page = request.args.get('per_page', 10, type=int) # 每页项目数，默认10

    paginated_commoditys = Commodity.query.paginate(page=page, per_page=per_page, error_out=False)

    commoditys = []
    for commodity in paginated_commoditys.items:
        subquery = ModelPrice.query.with_entities(ModelPrice.price).filter(ModelPrice.commodity_id == commodity.id).subquery()
        min_price = db.session.query(func.min(subquery.c.price)).scalar()
        commoditys.append({'number': commodity.number, 'title': commodity.title, 'description': commodity.description,'main_image':commodity.main_image,'price':min_price})

    # 创建分页信息的响应
    return jsonify({
        'total': paginated_commoditys.total,
        'pages': paginated_commoditys.pages,
        'page': page,
        'per_page': per_page,
        'prev_page': paginated_commoditys.prev_num,
        'next_page': paginated_commoditys.next_num,
        'has_prev': paginated_commoditys.has_prev,
        'has_next': paginated_commoditys.has_next,
        'commoditys': commoditys
    })


# 快捷命令
# ---------------------------------------------------------------------------------------
# 初始化数据
@app.cli.command()  # 注册为命令，可以传入 name 参数来自定义命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """初始化数据库"""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('已初始化数据库')  # 输出提示信息

# 生成测试数据
@app.cli.command()  # 注册为命令，可以传入 name 参数来自定义命令
def gendb():
    """生成测试数据"""
    faker = Faker(locale='zh_CN')
    #货物
    commodity = Commodity(
        number = faker.bothify('#########'),
        title = faker.text(max_nb_chars=10),
        description = faker.text(max_nb_chars=30),
        main_image = faker.image_url(),
        images = faker.json(data_columns={'images':['image_url', 'image_url', 'image_url']}, num_rows=1)
    )
    db.session.add(commodity)
    #型号和价格
    model_price = ModelPrice(
        type = faker.word(),
        price = faker.bothify('##.##'),
    )
    db.session.add(model_price)
    db.session.commit()
    commodity.models.append(model_price)
    db.session.commit()
    # 物流车
    expressage = Expressage(
        title = faker.text(max_nb_chars=5),
        description = faker.text(max_nb_chars=30),
        name = faker.name(),
        phone = faker.phone_number(),
        license_number = faker.license_plate()
    )
    db.session.add(expressage)
    db.session.commit()
    user = User(
        user_wechat = faker.vin(),
        phone = faker.phone_number()
    )
    db.session.add(user)
    consignee = Consignee(
        address = faker.address(),
        phone = faker.phone_number(),
        name = faker.name(),
        expressage_id = expressage.id
    )
    db.session.add(consignee)
    order = Order(
        number = faker.bothify('##################'),
        commodity_number = commodity.number,
        type = model_price.type,
        conut = faker.bothify('#'),
        address = consignee.address,
        phone = consignee.phone,
        expressage_id = consignee.expressage_id,
        name = consignee.name
    )
    db.session.add(order)
    db.session.commit()
    user.orders.append(order)
    user.consignees.append(consignee)
    db.session.commit()
    click.echo('已生成测试数据')  # 输出提示信息