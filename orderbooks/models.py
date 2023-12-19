from orderbooks import db

# DB设计
# 商品和分类的多对多关系
association_table = db.Table(
    'association',
    db.Column('good_id', db.Integer, db.ForeignKey('good.id')),
    db.Column('type_id', db.Integer, db.ForeignKey('type.id'))
)


# 商品数据结构
class Good(db.Model):
    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, unique=True)
    number = db.Column(db.Integer, nullable=False)  # 货号
    name = db.Column(db.String(80), nullable=False)  # 商品名称
    description = db.Column(db.Text)  # 商品描述
    main_image = db.Column(db.Text)  # 主图
    description_images = db.Column(db.JSON)  # 商品照片

    models = db.relationship('ModelPrice')  # 型号和价格组，每个商品有不同的型号和售价
    types = db.relationship(
        'Type', secondary=association_table, back_populates='goods')  # 每个商品有多个所属分类


# 商品归属的分类
class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, unique=True)
    name = db.Column(db.String(20), nullable=False, unique=True)  # 商品分类名称
    type_image_url = db.Column(db.Text, nullable=False)  # 分类的展示的图标

    goods = db.relationship(
        'Good', secondary=association_table, back_populates='types')  # 每个分类下有多个产品


# 商品的型号和价格
class ModelPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, unique=True)
    model = db.Column(db.String(20), nullable=False)  # 型号
    price = db.Column(db.Float, nullable=False)  # 价格

    good_id = db.Column(db.Integer, db.ForeignKey('good.id'))  # 外键-所属的商品


# 用户信息，需要对接微信openID
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, unique=True)
    user_wechat = db.Column(db.Text)  # 微信ID
    phone = db.Column(db.Integer)  # 手机号
    is_wholesale = db.Column(db.Boolean, default=False)  # 是否是批发商

    orders = db.relationship('Order')  # 每个用户有自己的订单信息
    consignees = db.relationship('Consignee')  # 每个用户有自己的地址信息
    carts = db.relationship('Cart')  # 每个用户有自己的购物车信息


# 订单信息
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, unique=True)
    number = db.Column(db.Integer, nullable=False)  # 订单号
    good_id = db.Column(db.Integer, nullable=False)  # 商品ID
    model_id = db.Column(db.Integer, nullable=False)  # 型号ID
    count = db.Column(db.Integer, nullable=False)  # 数量
    address = db.Column(db.Text, nullable=False)  # 地址
    phone = db.Column(db.Integer, nullable=False)  # 手机
    expressage_id = db.Column(db.Integer, nullable=False)  # 关联的物流车
    name = db.Column(db.String, nullable=False,)  # 收件人
    # 订单状态，1:等待确认，2：备货中，3，已发货,0:已取消订单
    status = db.Column(db.Integer, nullable=False, default=1)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 外键-所属的用户


# 收获地址信息
class Consignee(db.Model):
    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, unique=True)
    address = db.Column(db.Text, nullable=False)  # 地址
    phone = db.Column(db.Integer, nullable=False)  # 手机
    name = db.Column(db.String, nullable=False)  # 收件人
    expressage_id = db.Column(db.Integer, nullable=False)  # 地址关联的物流车

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 外键-所属的用户


# 物流车信息
class Expressage(db.Model):
    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, unique=True)

    name = db.Column(db.String(80), nullable=False)  # 物流名字
    description = db.Column(db.Text)  # 介绍
    contact_person = db.Column(db.String(80), nullable=False)  # 联系人
    phone = db.Column(db.Integer, nullable=False)  # 手机
    license_number = db.Column(db.String, nullable=False)  # 车牌号


# 购物车
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, unique=True)
    good_id = db.Column(db.Integer, nullable=False)  # 商品ID
    model_id = db.Column(db.Integer, nullable=False)  # 型号ID
    count = db.Column(db.Integer, nullable=False)  # 数量

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 外键-所属的用户


# 首页Banner图
class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, unique=True)
    image = db.Column(db.Text)  # banner图


# 首页模块开关
class HomeShowStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, unique=True)
    banner_show_status = db.Column(
        db.Boolean, nullable=False, default=False)  # Banner开启状态
    type_show_status = db.Column(db.Boolean, nullable=False,
                                 default=False)  # 分类展示开启状态
