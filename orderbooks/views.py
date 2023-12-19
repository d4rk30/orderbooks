from orderbooks import app, db
from flask import request,jsonify,url_for
from orderbooks.models import Good, ModelPrice, HomeSwitch
from sqlalchemy import func

# 首页开关状态
@app.route('/api/home_status')
def get_home_status():
    home_switch_record = HomeSwitch.query.get(1)
    return jsonify({
        'banner_switch':home_switch_record.banner_status,
        'type_switch':home_switch_record.type_status
    })

@app.route('/api/type')
def get_type():
    page = request.args.get('page', 1, type=int)         # 页数，默认为第1页
    per_page = request.args.get('per_page', 10, type=int) # 每页项目数，默认10
    good_type = [
        {"typename":"保暖系列","image_url":url_for('static',_external=True, filename='type1.jpg')},
        {"typename":"运动裤","image_url":url_for('static', _external=True,filename='type2.jpg')},
        {"typename":"打底小衫","image_url":url_for('static', _external=True,filename='type3.jpg')},
        {"typename":"羊绒系列","image_url":url_for('static', _external=True,filename='type4.jpg')},
    ]
    # 创建分页信息的响应
    return jsonify({
        'good_type': good_type
    })

# 获取货物信息
@app.route('/api/goods')
def get_goods():
    page = request.args.get('page', 1, type=int)         # 页数，默认为第1页
    per_page = request.args.get('per_page', 10, type=int) # 每页项目数，默认10

    paginated_goods = Good.query.paginate(page=page, per_page=per_page, error_out=False)

    goods = []
    for good in paginated_goods.items:
        subquery = ModelPrice.query.with_entities(ModelPrice.price).filter(ModelPrice.good_id == good.id).subquery()
        min_price = db.session.query(func.min(subquery.c.price)).scalar()
        goods.append({'id':good.id,'number': good.number, 'name': good.name, 'description': good.description,'main_image':good.main_image,'price':min_price})

    # 创建分页信息的响应
    return jsonify({
        'total': paginated_goods.total,
        'pages': paginated_goods.pages,
        'page': page,
        'per_page': per_page,
        'prev_page': paginated_goods.prev_num,
        'next_page': paginated_goods.next_num,
        'has_prev': paginated_goods.has_prev,
        'has_next': paginated_goods.has_next,
        'goods': goods
    })

# 获取货物详情

# 添加到购物车

# 获取购物车信息





# 下单-下单后返回订单详情页

# 获取订单列表

# 获取订单详情

# 取消订单，如果订单已经发货，则无法取消

# 查看个人收货地址

# 创建收获地址

# 更新收获地址