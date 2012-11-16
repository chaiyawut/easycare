from django.forms import widgets
from django.conf import settings
from django.template.defaulttags import mark_safe
from django.contrib.auth.models import User

class AutoCompleteWidget(widgets.MultiWidget):
    def __init__(self, attrs=None):
        widget_list = (widgets.Textarea(attrs=attrs),
                       widgets.Textarea(attrs=attrs),
                       widgets.Textarea(attrs=attrs))
        super(AutoCompleteWidget, self).__init__(widget_list, attrs)

    def decompress(self, value):
        """
        Accepts a single value which it then extracts enough values to
        populate the various widgets.
        
        We'll provide the id for the hidden input and a user
        representable string for the shown input field.
        """
        if value:
            return value.split("|")
        return ['', '', '']

    def render(self, name, value, attrs=None):
        """
        Converts the widget to an html representation of itself.
        """
        output = super(AutoCompleteWidget, self).render(name, value, attrs)
        return output


        
