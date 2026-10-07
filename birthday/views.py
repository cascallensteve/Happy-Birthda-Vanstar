from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import BirthdayWish


def home(request):
    """Main birthday page"""
    wishes = BirthdayWish.objects.all().order_by('-created_at')
    context = {
        'wishes': wishes,
    }
    return render(request, 'birthday/home.html', context)


@csrf_exempt
def submit_wish(request):
    """Handle birthday wish submission via AJAX (JSON or form)"""
    if request.method == 'POST':
        # Support both JSON and form data
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                name = data.get('name')
                message = data.get('message')
            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
        else:
            name = request.POST.get('name')
            message = request.POST.get('message')

        if name and message:
            wish = BirthdayWish.objects.create(name=name, message=message)
            return JsonResponse({
                'success': True,
                'message': 'Wish submitted successfully!',
                'wish': {
                    'id': wish.id,
                    'name': wish.name,
                    'message': wish.message,
                    'created_at': wish.created_at.strftime('%b %d, %Y %H:%M')
                }
            })
        else:
            return JsonResponse({'success': False, 'message': 'Please fill in all fields'}, status=400)

    elif request.method == 'GET':
        wishes = BirthdayWish.objects.all()
        wishes_data = [
            {
                'id': wish.id,
                'name': wish.name,
                'message': wish.message,
                'created_at': wish.created_at.strftime('%b %d, %Y %H:%M')
            }
            for wish in wishes
        ]
        return JsonResponse({'success': True, 'wishes': wishes_data})

    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


def admin_login(request):
    """Admin login page"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'birthday/admin_login.html')


@login_required
def admin_dashboard(request):
    """Admin dashboard showing all wishes"""
    wishes = BirthdayWish.objects.all()
    total_wishes = wishes.count()
    unique_users = wishes.values('name').distinct().count()

    from django.utils import timezone
    from datetime import datetime
    today = timezone.now().date()
    today_wishes = wishes.filter(created_at__date=today).count()

    context = {
        'wishes': wishes,
        'total_wishes': total_wishes,
        'unique_users': unique_users,
        'today_wishes': today_wishes,
    }

    return render(request, 'birthday/admin_dashboard.html', context)


@csrf_exempt
@login_required
def delete_wish(request, wish_id):
    """Delete a wish via AJAX or form"""
    if request.method == 'POST':
        try:
            wish = BirthdayWish.objects.get(id=wish_id)
            wish.delete()
            if request.content_type == 'application/json':
                return JsonResponse({'success': True, 'message': 'Wish deleted successfully'})
            messages.success(request, 'Wish deleted successfully')
        except BirthdayWish.DoesNotExist:
            if request.content_type == 'application/json':
                return JsonResponse({'success': False, 'message': 'Wish not found'}, status=404)
            messages.error(request, 'Wish not found')

    if request.content_type == 'application/json':
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
    return redirect('admin_dashboard')


@login_required
def admin_logout(request):
    """Admin logout"""
    logout(request)
    return redirect('home')

