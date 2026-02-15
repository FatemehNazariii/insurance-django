from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, MenuCategory, MenuItem, InsuranceCard, 
    DamageStep, InsuranceCompany, Inquiry, DamageReport, 
    InsuranceInfo, Feature, FAQ, TrustStep, InsuranceBenefit, 
    Order, Installment, InsuranceRate, CarBrand, CarModel,
    MotorcycleBrand, MotorcycleModel,
)

# --- تنظیمات هدر پنل ادمین ---
admin.site.site_header = "پنل مدیریت بیمه ایمنو"
admin.site.site_title = "ایمنو"
admin.site.index_title = "خوش آمدید"

# --- مدیریت کاربران ---
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('mobile', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('mobile', 'password')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name', 'email')}),
        ('دسترسی‌ها', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('تاریخ‌ها', {'fields': ('last_login', 'date_joined')}),
    )
    search_fields = ('mobile',)
    ordering = ('mobile',)

# --- اینلاین‌ها ---
class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1

class InsuranceBenefitInline(admin.TabularInline):
    model = InsuranceBenefit
    extra = 2

class InsuranceRateInline(admin.TabularInline):
    model = InsuranceRate
    extra = 0
    verbose_name_plural = "نرخ‌های این شرکت"
    can_delete = True

class InstallmentInline(admin.TabularInline):
    model = Installment
    extra = 0
    readonly_fields = ['amount', 'due_date', 'is_paid']
    can_delete = False

# --- مدیریت شرکت‌های بیمه ---
@admin.register(InsuranceCompany)
class InsuranceCompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'display_wealth', 'get_total_sales', 'get_orders_count', 'order']
    list_editable = ['order']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [InsuranceRateInline]

    def get_total_sales(self, obj):
        # بدنه تابع (یک مرحله تورفتگی بیشتر)
        data = obj.orders.filter(status='paid').aggregate(total=Sum('price'))
        total = data['total'] or 0
        price_string = f"{int(total):,}"
        return format_html('<b style="color: #2e7d32;">{} تومان</b>', price_string)
    
    get_total_sales.short_description = "مجموع فروش (موفق)"

    def get_orders_count(self, obj):
        return obj.orders.count()
    
    get_orders_count.short_description = "تعداد سفارشات"

    def display_wealth(self, obj):
        level = int(obj.wealth_level or 0)
        stars = "⭐" * level
        return format_html('<span title="سطح {}">{}</span>', level, stars)
    
    display_wealth.short_description = "سطح توانگری"
    
# --- مدیریت سفارشات ---
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'get_user_full_name', 'display_company', 
        'insurance', 'price', 'payment_type', 
        'get_remaining_status', 'status'
    ]
    list_filter = ['insurance_company', 'status', 'payment_type', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'national_code', 'insurance_company__name']
    inlines = [InstallmentInline]

    def display_company(self, obj):
        if obj.insurance_company and obj.insurance_company.logo:
            return format_html(
                '<img src="{}" style="width:25px; height:25px; object-fit:contain; margin-left:5px;"> {}',
                obj.insurance_company.logo.url, obj.insurance_company.name
            )
        return obj.insurance_company.name if obj.insurance_company else "---"
    display_company.short_description = "شرکت بیمه"

    def get_user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_user_full_name.short_description = "مشتری"

    def get_remaining_status(self, obj):
        if obj.payment_type == 'installment':
            remaining = obj.installments.filter(is_paid=False).count()
            return format_html('<span style="color: #d32f2f;">{} قسط مانده</span>', remaining)
        return "نقدی"
    get_remaining_status.short_description = "وضعیت اقساط"

@admin.register(InsuranceCard)
class InsuranceCardAdmin(admin.ModelAdmin):
    inlines = [InsuranceBenefitInline]
    list_display = ['title', 'category', 'order']
    list_filter = ['category']

@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    inlines = [MenuItemInline]
    list_display = ['name', 'order']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'category', 'order']
    list_filter = ['category']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title']

@admin.register(CarBrand)
class CarBrandAdmin(admin.ModelAdmin): 
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'base_price', 'fuel_type')
    list_filter = ('brand', 'fuel_type')
    search_fields = ('name', 'brand__name')
    list_editable = ('base_price', 'fuel_type')


@admin.register(MotorcycleBrand)
class MotorcycleBrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(MotorcycleModel)
class MotorcycleModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'base_price')
    list_filter = ('brand',)
    search_fields = ('name', 'brand__name')
    list_editable = ('base_price',)

# --- اطلاعات بیمه با اسلاگ ---
@admin.register(InsuranceInfo)
class InsuranceInfoAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}

# ثبت مدل‌های باقی‌مانده
admin.site.register([Feature, FAQ, TrustStep, DamageStep, Inquiry, DamageReport])