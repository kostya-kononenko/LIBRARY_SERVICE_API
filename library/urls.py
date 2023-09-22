from rest_framework import routers

from library.views import BookViewSet, CategoryViewSet

router = routers.DefaultRouter()
router.register("book", BookViewSet)
router.register("category", CategoryViewSet)


urlpatterns = router.urls

app_name = "library"