import { createRouter, createWebHashHistory } from 'vue-router'
import Commodity from '../components/Commodity.vue'
import Detail from '../components/Detail.vue'
import Shopper from '../components/Shopper.vue'
import Login from '../components/Login.vue'
import Order from '../components/Order.vue'
import PaymentResult from '../components/PaymentResult.vue'
import PetProfile from '../components/PetProfile.vue'
import Error from '../components/Error.vue'
import AdminLayout from '../components/admin/AdminLayout.vue'
import AdminDashboard from '../components/admin/AdminDashboard.vue'
import AdminProducts from '../components/admin/AdminProducts.vue'
import AdminInventory from '../components/admin/AdminInventory.vue'
import AdminOrders from '../components/admin/AdminOrders.vue'
import AdminAfterSales from '../components/admin/AdminAfterSales.vue'
import AdminUsers from '../components/admin/AdminUsers.vue'
import AdminSystemLogs from '../components/admin/AdminSystemLogs.vue'
import SuperAdminLayout from '../components/admin/SuperAdminLayout.vue'
import SuperAdminDashboard from '../components/admin/SuperAdminDashboard.vue'

// 定义路由
const routes = [
    { path: '/', redirect: '/commodity' },
    { path: '/commodity', component: Commodity, meta: { title: '宠物好物大厅' } },
    { path: '/commodity/detail/:id', component: Detail, meta: { title: '宠物好物详情' } },
    { path: '/login', component: Login, meta: { title: '宠物号登录' } },
    { path: '/shopper', component: Shopper, meta: { title: '我的地址档' } },
    { path: '/orders', component: Order, meta: { title: '我的流转单' } },
    { path: '/payment-result', component: PaymentResult, meta: { title: '支付结果' } },
    { path: '/pets', component: PetProfile, meta: { title: '我的宠物档案' } },
    // 商家管理后台（嵌套路由）
    {
        path: '/admin-panel',
        component: AdminLayout,
        meta: { title: '商家管理后台', requiresAdmin: true },
        redirect: '/admin-panel/dashboard',
        children: [
            { path: 'dashboard', component: AdminDashboard, meta: { title: '数据看板' } },
            { path: 'products', component: AdminProducts, meta: { title: '商品管理' } },
            { path: 'inventory', component: AdminInventory, meta: { title: '库存管理' } },
            { path: 'orders', component: AdminOrders, meta: { title: '订单管理' } },
            { path: 'aftersales', component: AdminAfterSales, meta: { title: '售后管理' } },
            // 超管专属路由（兼容旧入口，会被路由守卫重定向到 super-admin）
            { path: 'users', component: AdminUsers, meta: { title: '用户管理', requiresSuperuser: true } },
            { path: 'system-logs', component: AdminSystemLogs, meta: { title: '系统日志', requiresSuperuser: true } },
        ]
    },
    // 系统管理员层级后台（独立与商家后台分离）
    {
        path: '/super-admin',
        component: SuperAdminLayout,
        meta: { title: '系统管理员后台', requiresSuperuser: true },
        redirect: '/super-admin/dashboard',
        children: [
            { path: 'dashboard', component: SuperAdminDashboard, meta: { title: '平台总览', requiresSuperuser: true } },
            { path: 'users', component: AdminUsers, meta: { title: '用户管理', requiresSuperuser: true } },
            { path: 'system-logs', component: AdminSystemLogs, meta: { title: '系统日志', requiresSuperuser: true } },
        ]
    },
    // 路由匹配
    { path: '/:pathMatch(.*)*', component: Error, meta: { title: '页面丢失' } },
]

// 创建路由对象
const router = createRouter({
    // 设置历史记录模式
    history: createWebHashHistory(),
    // routes: routes的缩写
    routes,
})

// 路由守卫：管理后台仅限 is_staff 用户
router.beforeEach((to, from, next) => {
    if (to.meta.requiresAdmin) {
        const userInfo = JSON.parse(localStorage.getItem('pet_user') || '{}')
        if (!userInfo.is_staff && !userInfo.is_superuser) {
            next('/login')
            return
        }
    }
    // 超管专属页面鉴权
    if (to.meta.requiresSuperuser) {
        const userInfo = JSON.parse(localStorage.getItem('pet_user') || '{}')
        if (!userInfo.is_superuser) {
            // staff 用户重定向到商家看板，非登录用户重定向登录
            if (userInfo.username) {
                next('/admin-panel/dashboard')
            } else {
                next('/login')
            }
            return
        }
    }
    next()
})

export default router

