import click

from orderbooks import app, db
from faker import Faker
from orderbooks.models import Good, ModelPrice, Expressage, Consignee, Cart, Order, User, HomeShowStatus, Type
from flask import url_for


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
    # Banner和分类展示状态
    if HomeShowStatus.query.get(1) == None:
        home_show_status = HomeShowStatus(
            id=1,
            banner_show_status=True,
            type_show_status=True
        )
        db.session.add(home_show_status)
        db.session.commit()
    # 分类
    if Type.query.get(1) == None:
        type1 = Type(
            name='保暖系列',
            type_image_url='http://192.168.31.102:5000/static/type1.jpg'
        )
        type2 = Type(
            name='运动裤',
            type_image_url='http://192.168.31.102:5000/static/type2.jpg'
        )
        type3 = Type(
            name='打底小衫',
            type_image_url='http://192.168.31.102:5000/static/type3.jpg'
        )
        type4 = Type(
            name='羊绒系列',
            type_image_url='http://192.168.31.102:5000/static/type4.jpg'
        )
        db.session.add(type1)
        db.session.add(type2)
        db.session.add(type3)
        db.session.add(type4)
        db.session.commit()
    # 商品
    good = Good(
        number=faker.bothify('#########'),
        name=faker.text(max_nb_chars=10),
        description=faker.text(max_nb_chars=30),
        main_image=url_for('static', filename='def.jpeg'),
        description_images=faker.json(data_columns={'description_images': [
                                      'image_url', 'image_url', 'image_url']}, num_rows=1)
    )
    db.session.add(good)
    # 型号和价格
    model_price = ModelPrice(
        model=faker.word(),
        price=faker.bothify('##.##'),
    )
    db.session.add(model_price)
    db.session.commit()
    good.models.append(model_price)
    db.session.commit()
    # 物流车
    expressage = Expressage(
        name=faker.text(max_nb_chars=5),
        description=faker.text(max_nb_chars=30),
        contact_person=faker.name(),
        phone=faker.phone_number(),
        license_number=faker.license_plate()
    )
    db.session.add(expressage)
    db.session.commit()
    user = User(
        user_wechat=faker.vin(),
        phone=faker.phone_number(),
        is_wholesale=False
    )
    db.session.add(user)
    consignee = Consignee(
        address=faker.address(),
        phone=faker.phone_number(),
        name=faker.name(),
        expressage_id=expressage.id
    )
    db.session.add(consignee)
    cart = Cart(
        good_id=good.id,
        model_id=model_price.id,
        count=faker.bothify('#')
    )
    db.session.add(cart)
    order = Order(
        number=faker.bothify('##################'),
        good_id=good.id,
        model_id=model_price.id,
        count=faker.bothify('#'),
        address=consignee.address,
        phone=consignee.phone,
        expressage_id=consignee.expressage_id,
        name=consignee.name
    )
    db.session.add(order)
    db.session.commit()
    user.orders.append(order)
    user.consignees.append(consignee)
    user.carts.append(cart)
    db.session.commit()
    click.echo('已生成测试数据')  # 输出提示信息
