"""Django urlpatterns declaration for ipa app."""

from django.templatetags.static import static
from django.urls import path
from django.views.generic import RedirectView
from nautobot.apps.urls import NautobotUIViewSetRouter

from ipa import views

app_name = "ipa"
router = NautobotUIViewSetRouter()

router.register("ipaexamplemodel", views.IpaExampleModelUIViewSet)


urlpatterns = [
    path("docs/", RedirectView.as_view(url=static("ipa/docs/index.html")), name="docs"),
]

urlpatterns += router.urls
