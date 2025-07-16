"""Django API urlpatterns declaration for ipa app."""

from nautobot.apps.api import OrderedDefaultRouter

from ipa.api import views

router = OrderedDefaultRouter()
# add the name of your api endpoint, usually hyphenated model name in plural, e.g. "my-model-classes"
router.register("ipaexamplemodel", views.IpaExampleModelViewSet)

app_name = "ipa-api"
urlpatterns = router.urls
