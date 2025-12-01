from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from playground_api.views import (
    TransformerHeuristicCreateView,
    # Legacy v1.1.0 views (kept for backward compatibility)
    TransformerCategorizeV1_1_0View,
    TransformerEntitiesV1_1_0AnalyzeView,
    TransformerEntitiesV1_1_0ExtractView,
    TransformerEntitiesV1_1_0TestView,
    TransformerLogicV1_1_0CreateView,
    # Version-flexible views (support all OCSF versions)
    TransformerCategorizeView,
    TransformerEntitiesAnalyzeView,
    TransformerEntitiesExtractView,
    TransformerEntitiesTestView,
    TransformerLogicCreateView,
    # Utility views
    AuthDiagnosticView
)


urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('auth/diagnostic/', AuthDiagnosticView.as_view(), name='auth_diagnostic'),
    path('transformer/heuristic/create/', TransformerHeuristicCreateView.as_view(), name='transformer_heuristic_create'),

    # Legacy v1.1.0 endpoints (kept for backward compatibility)
    path('transformer/categorize/v1_1_0/', TransformerCategorizeV1_1_0View.as_view(), name='transformer_categorize_v1_1_0'),
    path('transformer/entities/v1_1_0/analyze/', TransformerEntitiesV1_1_0AnalyzeView.as_view(), name='transformer_entities_v1_1_0_analyze'),
    path('transformer/entities/v1_1_0/extract/', TransformerEntitiesV1_1_0ExtractView.as_view(), name='transformer_entities_v1_1_0_extract'),
    path('transformer/entities/v1_1_0/test/', TransformerEntitiesV1_1_0TestView.as_view(), name='transformer_entities_v1_1_0_test'),
    path('transformer/logic/v1_1_0/create/', TransformerLogicV1_1_0CreateView.as_view(), name='transformer_logic_v1_1_0_create'),

    # Version-flexible endpoints (support all OCSF versions via ocsf_version parameter)
    path('transformer/categorize/', TransformerCategorizeView.as_view(), name='transformer_categorize'),
    path('transformer/entities/analyze/', TransformerEntitiesAnalyzeView.as_view(), name='transformer_entities_analyze'),
    path('transformer/entities/extract/', TransformerEntitiesExtractView.as_view(), name='transformer_entities_extract'),
    path('transformer/entities/test/', TransformerEntitiesTestView.as_view(), name='transformer_entities_test'),
    path('transformer/logic/create/', TransformerLogicCreateView.as_view(), name='transformer_logic_create'),
]