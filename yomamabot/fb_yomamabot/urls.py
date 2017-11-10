from django.conf.urls import url
from .views import YoMamaBotView


urlpatterns = [
                  url(r'^9fe59bdd4f7f9a10b4dcc69e0bd54a04927499cbef63123808/?$', YoMamaBotView.as_view())
               ]
