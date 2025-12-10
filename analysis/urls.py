from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProcessedFeedbackViewSet,
    InsightViewSet,
    DashboardAnalyticsView,
    TopicAnalyticsView,
    ProductAnalyticsView
)

router = DefaultRouter()
router.register(r'processed-feedbacks', ProcessedFeedbackViewSet, basename='processed-feedback')
router.register(r'insights', InsightViewSet, basename='insight')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Dashboard Analytics
    path('dashboard/', DashboardAnalyticsView.as_view(), name='dashboard-analytics'),
    
    # Topic Analytics
    path('topics/<str:topic>/', TopicAnalyticsView.as_view(), name='topic-analytics'),
    
    # Product Analytics
    path('products/<str:product_name>/', ProductAnalyticsView.as_view(), name='product-analytics'),
]