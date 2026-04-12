import random
from decimal import Decimal
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import User, SysRole
from commodity.models import Category, Product, Inventory
from shopper.models import Address, OrderInfo, OrderItem, PetProfile, Cart
from aftersales.models import AfterSales

class Command(BaseCommand):
    help = 'PetMal数据种子初始化'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('[Init] Starting PetMall data seeding...'))

        try:
            with transaction.atomic():
                self.seed_roles_and_users()
                self.seed_categories_and_products()
                self.seed_orders_and_aftersales()
            
            self.stdout.write(self.style.SUCCESS('[Success] All data seeded successfully.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[Error] Seeding failed: {str(e)}'))

    def seed_roles_and_users(self):
        self.stdout.write('--- [1/3] 注入用户体系 ---')
        # 1. 创建角色
        admin_role, _ = SysRole.objects.get_or_create(role_code='ADMIN', defaults={'role_name': '超级管理员', 'description': '拥有最高权限'})
        user_role, _ = SysRole.objects.get_or_create(role_code='USER', defaults={'role_name': '普通买家', 'description': '前台购物用户'})

        # 2. 创建管理员 (admin / 123456xqy)
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                password='123456xqy',
                real_name='系统管理员',
                phone='13811112222',
                role=admin_role
            )
            self.stdout.write(f'  - Superuser created: admin')

        # 3. 创建测试用户 (复用你的张阿猫、李傻狗、王金鱼数据)
        users_data = [
            {'username': 'test1', 'real_name': '张阿猫', 'phone': '13800000001', 'pets': [('大黄', '狗', '柯基')]},
            {'username': 'test2', 'real_name': '李傻狗', 'phone': '13800000002', 'pets': [('咪咪', '猫', '布偶猫')]},
            {'username': 'test3', 'real_name': '王金鱼', 'phone': '13800000003', 'pets': [('泡泡', '鱼', '金鱼')]},
        ]

        for u_data in users_data:
            user, created = User.objects.get_or_create(
                username=u_data['username'],
                defaults={
                    'real_name': u_data['real_name'],
                    'phone': u_data['phone'],
                    'role': user_role
                }
            )
            if created:
                user.set_password('123456')
                user.save()
                self.stdout.write(f'  - Test user created: {user.username}')
                
                # 为用户创建地址
                Address.objects.get_or_create(
                    user=user,
                    receiver_name=u_data['real_name'],
                    defaults={
                        'receiver_phone': u_data['phone'],
                        'province': '北京市',
                        'city': '北京市',
                        'district': '朝阳区',
                        'detail_address': '宠物大道 8 单元 601 室',
                        'is_default': True
                    }
                )

                # 为用户创建宠物档案
                for p_name, p_type, breed in u_data['pets']:
                    PetProfile.objects.create(
                        user=user,
                        pet_name=p_name,
                        pet_type=p_type,
                        breed=breed,
                        gender=1,
                        size='MEDIUM'
                    )

    def seed_categories_and_products(self):
        self.stdout.write('--- [2/3] 注入商品与库存 ---')
        categories = ['汪喵主粮', '零食罐头', '日常消耗', '逗趣玩具', '出行牵引']
        cat_map = {}
        for idx, name in enumerate(categories):
            cat, _ = Category.objects.get_or_create(name=name, level=1, defaults={'sort_order': idx})
            cat_map[name] = cat

        # 核心商品字典 (整合你 test_init_data.py 中的精美语料)
        products_data = [
            {"cat": "汪喵主粮", "name": "全价无谷冻干鲜肉猫粮 2KG", "price": 149.00, "desc": "高蛋白低肠胃负担，加入8%冻干。"},
            {"cat": "汪喵主粮", "name": "金毛拉布拉多成犬天然狗粮 10KG", "price": 288.50, "desc": "深海鱼油添加，强健骨骼。"},
            {"cat": "汪喵主粮", "name": "幼猫断奶期专研营养奶糕", "price": 89.00, "desc": "好消化易吸收，帮助幼猫平稳度过。"},
            {"cat": "零食罐头", "name": "泰国进口金枪鱼虾仁猫罐头 85g*6罐", "price": 59.90, "desc": "大块鲜肉，真材实料。"},
            {"cat": "日常消耗", "name": "豆腐+膨润土混合猫砂 2.5KG*4包", "price": 69.90, "desc": "除臭力强，结团快。"},
            {"cat": "逗趣玩具", "name": "仙女棒羽毛铃铛逗猫棒", "price": 12.80, "desc": "激发猫咪狩猎本能。"},
            {"cat": "出行牵引", "name": "防爆冲一键锁止伸缩牵引绳 5米", "price": 58.00, "desc": "夜间反光，安全耐用。"}
        ]

        for i, pd in enumerate(products_data, 1):
            product, created = Product.objects.get_or_create(
                name=pd['name'],
                defaults={
                    'category': cat_map[pd['cat']],
                    'main_image': f'imgs/pd_{i}.jpg', # 关联本地下好的图
                    'price': Decimal(str(pd['price'])),
                    'old_price': Decimal(str(pd['price'] * 1.2)),
                    'description': pd['desc'],
                    'sales': random.randint(10, 500)
                }
            )
            # 初始化库存
            Inventory.objects.get_or_create(
                product=product,
                defaults={'current_quantity': random.randint(50, 200)}
            )
            if created:
                self.stdout.write(f'  - Product created: {pd["name"]}')

    def seed_orders_and_aftersales(self):
        self.stdout.write('--- [3/3] 注入交易流水与售后单 ---')
        users = User.objects.filter(role__role_code='USER')
        products = Product.objects.all()

        if not users.exists() or not products.exists():
            return

        for i in range(1, 11):
            user = random.choice(users)
            address = Address.objects.filter(user=user).first()
            p_sample = random.sample(list(products), random.randint(1, 3))
            
            order = OrderInfo.objects.create(
                order_no=f'ORD{timezone.now().strftime("%Y%m%d%H%M%S")}{i}',
                user=user,
                receiver_name=address.receiver_name if address else '测试收件人',
                receiver_phone=address.receiver_phone if address else '13800000000',
                receiver_address=f"{address.province}{address.city}{address.detail_address}" if address else '北京市朝阳区测试路',
                status=random.choice(['PAID', 'SHIPPED', 'COMPLETED']),
                total_amount=0
            )

            total = 0
            for p in p_sample:
                qty = random.randint(1, 2)
                subtotal = p.price * qty
                OrderItem.objects.create(
                    order=order,
                    product=p,
                    product_name=p.name,
                    product_price=p.price,
                    quantity=qty,
                    subtotal=subtotal
                )
                total += subtotal
            
            order.total_amount = total
            order.save()

            # 随机生成一个售后
            if i == 5:
                AfterSales.objects.create(
                    order=order,
                    user=user,
                    sales_type='REFUND',
                    reason='买错了，不想要了',
                    refund_amount=order.total_amount,
                    status='APPLYING'
                )
            
            self.stdout.write(f'  - Order created: {order.order_no} ({order.status})')
