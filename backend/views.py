# views.py
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse


def home(request):
    return render(request, 'home.html')  # Renders the home.html template

# backend/views.py

from django.shortcuts import render
from django.http import HttpResponse

def contact(request):
    if request.method == 'POST':
        # Get data from the form
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Print the message to the terminal
        print(f"New message from {name} ({email}): {message}")

        return render(request, 'thank_you.html')  # Redirect to a thank you page after submission
    
    return render(request, 'contact.html')

def thank_you(request):
    return render(request, 'thank_you.html')  # Render a thank you page