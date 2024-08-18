from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("", views.home_page, name="home"),
    path("instractor/", views.Instractor_portal, name="instractor_dashboard"),
    path("student/", views.Student_dashboard, name="student_dashboard"),
    path("accounts/login/", views.CustomLoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("partners/", views.partners, name="partners"),
    path("faqs/", views.faqs, name="faqs"),
    path("about/", views.about, name="about"),
    path("terms/", views.terms, name="terms"),
    path("privacy", views.privacy, name="privacy"),
    path("contacts/", views.contacts, name="contacts"),
    path("students_register/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/student_admision", views.student_admision, name="student_admision"),
    path(
        "admin/student_info/<int:student_id>/", views.student_info, name="student_info"
    ),
    path(
        "admin/student_payment/<int:enrollment_id>/",
        views.student_payment,
        name="student_payment",
    ),
    path("admin/perfomance", views.performance, name="perfomance"),
    path("admin/add_performance", views.add_performance, name="add_performance"),
    path(
        "admin/student_info_pdf/<int:student_id>/",
        views.student_info_pdf,
        name="student_info_pdf",
    ),
    path(
        "student_register_pdf/", views.student_register_pdf, name="student_register_pdf"
    ),
    path("home/courses", views.home_courses, name="courses"),
    path("home/courses/<int:id>/", views.home_courses, name="courses"),
    path(
        "home/courses/course_about/<int:id>/<str:name>/",
        views.course_about,
        name="course_about",
    ),
    path("home/subscription", views.subscription, name="subscription"),
    path("mine/", views.ManageCourseListView.as_view(), name="manage_course_list"),
    path("create/", views.CourseCreateView.as_view(), name="course_create"),
    path("<pk>/edit/", views.CourseUpdateView.as_view(), name="course_edit"),
    path("<pk>/delete/", views.CourseDeleteView.as_view(), name="course_delete"),
    path(
        "<pk>/module/",
        views.CourseModuleUpdateView.as_view(),
        name="course_module_update",
    ),
    path(
        "module/<int:module_id>/content/<model_name>/create/",
        views.ContentCreateUpdateView.as_view(),
        name="module_content_create",
    ),
    path(
        "module/<int:module_id>/content/<model_name>/<id>/",
        views.ContentCreateUpdateView.as_view(),
        name="module_content_update",
    ),
    path(
        "content/<int:id>/delete/",
        views.ContentDeleteView.as_view(),
        name="module_content_delete",
    ),
    path(
        "module/<int:module_id>/",
        views.ModuleContentListView.as_view(),
        name="module_content_list",
    ),
    path("module/order/", views.ModuleOrderView.as_view(), name="module_order"),
    path("content/order/", views.ContentOrderView.as_view(), name="content_order"),
    path(
        "subject/",
        views.CourseListView.as_view(),
        name="course_list",
    ),
    path(
        "subject/<slug:subject>/",
        views.CourseListView.as_view(),
        name="course_list_subject",
    ),
    path(
        "subject/course/<slug:slug>/",
        views.CourseDetailView.as_view(),
        name="course_detail",
    ),
    # path(
    #     "student/enroll-course/",
    #     views.StudentEnrollCourseView.as_view(),
    #     name="student_enroll_course",
    # ),
    path(
        "student/courses/",
        views.StudentCourseListView.as_view(),
        name="student_course_list",
    ),
    path(
        "course/<pk>/",
        views.StudentCourseDetailView.as_view(),
        name="student_course_detail",
    ),
    path(
        "course/<pk>/<module_id>/",
        views.StudentCourseDetailView.as_view(),
        name="student_course_detail_module",
    ),
    # path("check_data/", views.check_data, name="check_data"),
]
