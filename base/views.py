from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy

from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from random import *
from random import randrange
from django.core.mail import send_mail
from django.contrib import messages

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import Task

from .forms import FeedbackForm

import requests
import geocoder
import folium

class CustomLoginView(LoginView):
	template_name = 'base/login.html'
	fields = '__all__'
	redirect_authenticated_user = True

	def get_success_url(self):
		return reverse_lazy('tasks')

class RegisterPage(FormView):
	template_name = 'base/register.html'
	form_class = UserCreationForm
	redirect_authenticated_user = True
	success_url = reverse_lazy('tasks')

	def form_valid(self, form):
		user = form.save()
		if user is not None:
			login(self.request, user)
		return super(RegisterPage, self).form_valid(form)

	def get(self, *args, **kwargs):
		if self.request.user.is_authenticated:
			return redirect('tasks')
		return super(RegisterPage, self).get(*args, **kwargs)

class TaskList(LoginRequiredMixin, ListView):
	model = Task
	context_object_name = 'tasks'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['tasks'] = context['tasks'].filter(user=self.request.user)
		context['count'] = context['tasks'].filter(complete=False).count()

		search_input = self.request.GET.get('search-area') or ''
		if search_input:
			context['tasks'] = context['tasks'].filter(title__startswith=search_input)
		context['search_input'] = search_input

		return context
	


class TaskDetail(LoginRequiredMixin, DetailView):
	model = Task
	context_object_name = 'task'
	template_name = 'base/task.html'

class TaskCreate(LoginRequiredMixin, CreateView):
	model = Task
	fields = ['title', 'description', 'complete']
	success_url = reverse_lazy('tasks')

	def form_valid(self, form):
		form.instance.user = self.request.user
		return super(TaskCreate, self).form_valid(form)


class TaskUpdate(LoginRequiredMixin, UpdateView):
	model = Task
	fields = ['title', 'description', 'complete']
	success_url = reverse_lazy('tasks')

class DeleteView(LoginRequiredMixin, DeleteView):
	model = Task
	context_object_name = 'task'
	success_url = reverse_lazy('tasks')

def rnp(request):
	if request.method =="POST":
		un = request.POST.get("un")
		try:
			usr = User.objects.get(username=un)
			pw =""
			text = "123456789"
			for i in range(4):
				pw = pw + text[randrange(len(text))]
			print(pw)
			subject ="Welcome to kamal classes"
			text ="Ur password is " + str(pw)
			from_email ="aniket24aug22@gmail.com"
			to_email = [str(un)]
			send_mail(subject, text, from_email, to_email)
			usr.set_password(pw)
			usr.save()
			return redirect("login")
		except User.DoesNotExist:
			return render(request, "base/rnp.html", {"msg":"User Does Not Exists"})
	else:
		return render(request, "base/rnp.html")

def location(request):
	if request.user.is_authenticated:
		if request.POST.get("loc"):
			loc = request.POST.get("loc")
			try:
				lat_lng = geocoder.osm(loc)
				lat = lat_lng.lat
				lng = lat_lng.lng
				lat_lng = [lat, lng]
				f = folium.Figure(width=700, height=400)
				place = folium.Map(location=lat_lng, zoom_start=16).add_to(f)
				folium.Marker(lat_lng, tooltip=loc).add_to(place)
				place_html = place._repr_html_()
				return render(request, "base/location.html",{"msg":place_html})
			except Exception as e:
				return render(request, "base/location.html",{"msg":" Please Enter Correct Spelling of Location or co-ordinates "})
		else:	
			return render(request,"base/location.html")
	else:
		return redirect("login")

def news(request):
	if request.user.is_authenticated:
		if request.GET.get("btn"):
			try:
				a1 = "https://newsapi.org/v2/top-headlines"
				a2 = "?country=" + "in"
				a3 = "&apiKey=" + "dcf42dec7d614e778d3dcd8616ab8182"
				wa = a1 + a2 + a3
				res = requests.get(wa)
				data = res.json()
				info = data["articles"]
				return render(request, "base/news.html", {"msg":info})

			except Exception as e:
				print("issue", e)
				return render(request, "base/news.html", {"msg":info})
		else:	
			return render(request, "base/news.html")
	else:
		return redirect("login")

def feedback_form(request):
	if request.user.is_authenticated:
		if request.method == 'POST':
			form = FeedbackForm(request.POST)

			if form.is_valid():
				form.save()
				return render(request, 'base/thanks.html')
		else:
			form = FeedbackForm()
			return render(request, 'base/feedback_form.html', {'form': form})
	else:
		return redirect("login")