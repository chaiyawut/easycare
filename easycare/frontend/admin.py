from django.contrib import admin
from frontend.models import *

admin.site.register(Patient)
admin.site.register(Record)
admin.site.register(Response)
admin.site.register(Drug)
admin.site.register(Pressure)
admin.site.register(Weight)

