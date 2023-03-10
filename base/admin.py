from django.contrib import admin
from .models import Task
from .models import Feedback

class FeedbackAdmin(admin.ModelAdmin):
	list_display = ("name","fbdt")
	list_filter = ("fbdt",)

	class Meta:
		model = Feedback

admin.site.register(Feedback,FeedbackAdmin)
admin.site.register(Task)
