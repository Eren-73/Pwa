# d:\Freelance\Python_Dev\Pwa\devis_app\views_theme.py
# Vue HTMX pour le theme toggle avec debug
# RELEVANT FILES: devis_app/urls.py, devis_app/templates/base.html

from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

@require_POST
def toggle_theme(request):
    """Toggle theme via HTMX avec debug terminal"""
    
    try:
        # Parse le body
        data = json.loads(request.body)
        current_theme = data.get('current_theme', 'light')
        new_theme = 'dark' if current_theme == 'light' else 'light'
        
        # 🔍 DEBUG TERMINAL
        print("\n" + "="*60)
        print("🎨 THEME TOGGLE REQUEST")
        print("="*60)
        print(f"📥 Current theme: {current_theme}")
        print(f"📤 New theme: {new_theme}")
        print(f"🌐 User Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')[:50]}...")
        print(f"🔗 Referer: {request.META.get('HTTP_REFERER', 'None')}")
        print(f"🕐 Method: {request.method}")
        print("="*60 + "\n")
        
        return JsonResponse({
            'success': True,
            'theme': new_theme,
            'message': f'Theme changed to {new_theme}'
        })
        
    except Exception as e:
        # 🔴 ERROR DEBUG
        print("\n" + "="*60)
        print("❌ THEME TOGGLE ERROR")
        print("="*60)
        print(f"Error: {str(e)}")
        print(f"Request body: {request.body}")
        print("="*60 + "\n")
        
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


def get_theme(request):
    """Get current theme from cookie"""
    theme = request.COOKIES.get('theme', 'light')
    
    print(f"🎨 Get theme: {theme}")
    
    return JsonResponse({'theme': theme})
