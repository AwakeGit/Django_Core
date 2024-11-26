from django.urls import path

from apps.docs.views import (
    AnalyzeFileView,
    DeleteFileView,
    GetTextView,
    MainPageView,
    UploadPhotosView,
)

urlpatterns = [
    path("", MainPageView.as_view(), name="main"),
    path("upload/", UploadPhotosView.as_view(), name="upload_photos"),
    path("analyze/<int:doc_id>/", AnalyzeFileView.as_view(), name="analyze_file"),
    path("get_text/<int:doc_id>/", GetTextView.as_view(), name="get_text"),
    path("delete/<int:doc_id>/", DeleteFileView.as_view(), name="delete_file"),
]
