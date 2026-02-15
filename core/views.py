from django.shortcuts import render, redirect,  get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
from .models import InsuranceCard, DamageStep, InsuranceCompany, Inquiry, DamageReport, InsuranceInfo, Feature, FAQ, TrustStep, MenuCategory, MenuItem, Order, Installment, CarBrand, CarModel, InsuranceRate, MotorcycleBrand, MotorcycleModel
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, get_user_model, logout
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from django.db.models import F
from core.services.pricing_service import PricingService


User = get_user_model()
def home(request):
    cards = InsuranceCard.objects.all()[:6]
    all_insurances = InsuranceCard.objects.all()
    steps = DamageStep.objects.all().order_by('number')
    companies = InsuranceCompany.objects.all()
    insurance_infos = InsuranceInfo.objects.all()
    faqs = FAQ.objects.all().order_by('order')
    features_list = Feature.objects.all().order_by('order') 
    trust_steps = TrustStep.objects.all().order_by('order')
    brands = CarBrand.objects.all()
    nav_categories = MenuCategory.objects.prefetch_related('items').all()

    context = {
        'insurance_cards': cards,
        'all_insurances': all_insurances,
        'damage_steps': steps,
        'companies': companies,
        'insurance_infos': insurance_infos,
        'features': features_list,
        'faqs': faqs,
        'trust_steps': trust_steps,
        'nav_categories': nav_categories,
        'brands': brands, 
    }
    
    return render(request, 'home.html', context)
    return render(request, 'index.html', {'all_insurances': all_insurances})

def submit_inquiry(request):
    if request.method == "POST":
        phone = request.POST.get('phone_number')
        if phone:
            Inquiry.objects.create(phone_number=phone)
            messages.success(request, "درخواست مشاوره شما ثبت شد.")
    return redirect('/')

def submit_damage(request):
    if request.method == "POST":
        ins_type = request.POST.get('insurance_type')
        company_id = request.POST.get('company')
        address = request.POST.get('address')
        phone = request.POST.get('phone_number')
        
        if phone and company_id:
            try:
                company = InsuranceCompany.objects.get(id=company_id)
                DamageReport.objects.create(
                    insurance_type=ins_type,
                    company_name=company,
                    address=address,
                    phone_number=phone
                )
                messages.success(request, "درخواست خسارت شما با موفقیت ثبت شد.")
            except InsuranceCompany.DoesNotExist:
                messages.error(request, "شرکت بیمه معتبر نیست.")
    return redirect('/')

@login_required
def dashboard(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    mobile = getattr(request.user, 'mobile', request.user.username)
    orders = Order.objects.filter(user=request.user).prefetch_related('installments').order_by('-created_at')
   
    context = {
        'mobile': mobile,
        'orders': orders,
        'orders_count': orders.count(),
    }
    return render(request, 'core/dashboard.html', context)
    return render(request, 'core/dashboard.html', {'orders': orders})

@csrf_exempt
def check_user_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mobile = data.get('mobile')
            if not mobile:
                return JsonResponse({'exists': False, 'error': 'شماره وارد نشده'}, status=400)
            user_exists = User.objects.filter(mobile=mobile).exists()
            return JsonResponse({'exists': user_exists})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
@csrf_exempt
def auth_user_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mobile = data.get('mobile')
            password = data.get('password')
            
            if not mobile or not password:
                return JsonResponse({'status': 'error', 'message': 'شماره موبایل و رمز عبور اجباری هستند'}, status=400)
            user = authenticate(request, mobile=mobile, password=password)
            
            if user is not None:
                login(request, user)
                return JsonResponse({'status': 'success', 'action': 'login'})
            if not User.objects.filter(mobile=mobile).exists():
                first_name = data.get('first_name', '')
                last_name = data.get('last_name', '')
                new_user = User.objects.create_user(
                    mobile=mobile,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_staff=False,    
                    is_superuser=False 
                )
                
                from .models import SiteUser
                SiteUser.objects.get_or_create(phone_number=mobile)
                
                login(request, new_user)
                return JsonResponse({'status': 'success', 'action': 'register'})
            else:
                return JsonResponse({'status': 'error', 'message': 'رمز عبور اشتباه است یا این کاربر دسترسی ندارد'}, status=401)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        
@csrf_exempt
def user_logout(request):
    if request.method == 'POST':
        logout(request)
    return redirect('/')



@login_required
def create_order(request, card_slug):
    card = get_object_or_404(InsuranceCard, slug=card_slug)
    pay_type = request.GET.get('type', 'cash') 
    total_price = card.price 
    order = Order.objects.create(
        user=request.user,
        insurance=card,
        price=total_price,
        payment_type=pay_type,
        status='pending',
        installments_count=4 if pay_type == 'installment' else 0
    )
    if pay_type == 'installment':
        installment_amount = total_price / 4
        for i in range(1, 5):
            Installment.objects.create(
                order=order,
                amount=installment_amount,
                due_date=timezone.now().date() + timedelta(days=30*i)
            )

    return redirect('core:order_detail', order_id=order.id)

def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'core/order_detail.html', {'order': order})


@login_required
def fake_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.is_paid = True
    order.status = 'paid'
    order.save()
    first_installment = order.installments.first()
    if first_installment:
        first_installment.is_paid = True
        first_installment.payment_date = timezone.now()
        first_installment.save()

    return render(request, 'core/payment_success.html', {'order': order})



def _get_insurance_detail_context(insurance):
    """ساخت context مشترک برای صفحه جزئیات بیمه."""
    if 'third' in insurance.slug.lower() or 'saless' in insurance.slug.lower():
        i_type = 'third_party'
    elif 'body' in insurance.slug.lower() or 'badaneh' in insurance.slug.lower():
        i_type = 'body'
    else:
        i_type = insurance.slug
    rates = InsuranceRate.objects.filter(
        insurance_type=i_type,
        company__isnull=False
    ).select_related('company').annotate(price_toman=F('base_fee') / 10).order_by('price_toman')
    is_motorcycle = 'موتور' in (insurance.title or '') or 'motor' in (insurance.slug or '').lower()
    return {
        'insurance': insurance,
        'rates': rates,
        'brands': CarBrand.objects.all(),
        'motorcycle_brands': MotorcycleBrand.objects.all(),
        'faqs': FAQ.objects.all(),
        'features': Feature.objects.all(),
        'companies': InsuranceCompany.objects.all(),
        'is_motorcycle': is_motorcycle,
        'vehicle_label': 'موتور' if is_motorcycle else 'خودرو',
    }


def menu_item_page(request, slug):
    """صفحه مربوط به هر آیتم زیرمنو. اگر به کارت بیمه وصل باشد همان صفحه بیمه، وگرنه صفحه با عنوان و توضیحات."""
    item = get_object_or_404(MenuItem, slug=slug)
    if item.insurance_card:
        context = _get_insurance_detail_context(item.insurance_card)
        return render(request, 'insurance_detail.html', context)
    context = {'item': item}
    return render(request, 'core/menu_item_page.html', context)


def insurance_detail(request, slug):
    insurance = get_object_or_404(InsuranceCard, slug=slug)
    context = _get_insurance_detail_context(insurance)
    return render(request, 'insurance_detail.html', context)


def insurance_info_detail(request, slug):
    """صفحه جزئیات هر آیتم اطلاعات بیمه (InsuranceInfo) با اسلاگ."""
    info = get_object_or_404(InsuranceInfo, slug=slug)
    context = {'info': info}
    return render(request, 'core/insurance_info_detail.html', context)


def company_detail(request, slug):
    """صفحه جزئیات هر شرکت بیمه با اسلاگ."""
    company = get_object_or_404(InsuranceCompany, slug=slug)
    rates = InsuranceRate.objects.filter(company=company).select_related('company')
    context = {'company': company, 'rates': rates}
    return render(request, 'core/company_detail.html', context)

def insurance_form(request):
    brands = CarBrand.objects.all()
    return render(request, 'your_template.html', {'brands': brands})

def get_models(request):
    brand_id = request.GET.get('brand_id')
    if not brand_id:
        return JsonResponse([], safe=False)
    models = CarModel.objects.filter(brand_id=brand_id).values('id', 'name', 'base_price')
    return JsonResponse(list(models), safe=False)

def get_motor_models(request):
    brand_id = request.GET.get('brand_id')
    if not brand_id:
        return JsonResponse([], safe=False)
    models = MotorcycleModel.objects.filter(brand_id=brand_id).values('id', 'name', 'base_price')
    return JsonResponse(list(models), safe=False)


@login_required
def submit_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            insurance = InsuranceCard.objects.first()
            if not insurance:
                return JsonResponse({'status': 'error', 'message': 'هیچ کارت بیمه‌ای یافت نشد'}, status=404)

            is_installment = "اقساط" in str(data.get('type'))
            count = 4  

            order = Order.objects.create(
                user=request.user,
                insurance=insurance,
                price=int(data.get('price', 0)),
                company_name=data.get('company'),
                plate_number=data.get('plate'),
                payment_type='installment' if is_installment else 'cash',
                installments_count=count if is_installment else 0,
                is_paid=True, 
                status='paid'
            )

            if is_installment:
                amount_per_installment = order.price // count
                for i in range(1, count + 1):
                    Installment.objects.create(
                        order=order,
                        amount=amount_per_installment,
                        due_date=timezone.now().date() + timedelta(days=30 * i),
                        is_paid=False
                    )
            
            return JsonResponse({'status': 'success', 'message': 'سفارش با موفقیت ثبت شد'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def calculate_prices_api(request):
    model_id = request.GET.get('model_id')
    year = int(request.GET.get('year', 1404))
    is_motor = request.GET.get('vehicle') == 'motor'

    if not model_id:
        return JsonResponse({'results': [], 'message': 'مدل انتخاب نشده است'}, status=400)

    try:
        if is_motor:
            vehicle_model = MotorcycleModel.objects.get(id=model_id)
        else:
            vehicle_model = CarModel.objects.get(id=model_id)
        ins_type = request.GET.get('type', 'body')
        rates = InsuranceRate.objects.filter(insurance_type=ins_type).select_related('company')

        results = []
        for rate in rates:
            base_toman = vehicle_model.base_price / 10
            from datetime import datetime
            current_year = datetime.now().year  
            age_factor = (current_year - year)
            final_price = (base_toman * (1 + age_factor)) * float(rate.car_value_coefficient) + float(rate.base_fee)
            results.append({
                'company_name': rate.company.name,
                'company_logo': rate.company.logo.url if rate.company.logo else '',
                'wealth_level': rate.company.wealth_level,
                'final_price': int(final_price),
                'installment_price': int((final_price * 1.05) / 6),
            })
        return JsonResponse({'results': results})
    except (CarModel.DoesNotExist, MotorcycleModel.DoesNotExist):
        return JsonResponse({'results': [], 'message': 'مدل یافت نشد'}, status=404)