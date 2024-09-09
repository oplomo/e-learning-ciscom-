from django.contrib import admin
from django import forms
from django.contrib.auth.models import Group
from .models import Course, Enrollment
from account.models import CustomUser
from django.contrib.auth.admin import UserAdmin

from .models import (
    Subject,
    Course,
    Module,
    Content,
    Text,
    File,
    Image,
    Video,
    Rct,
    Partners,
    Testimonials,
    Question,
    Answer,
    Enrollment,
    Payment,
    Perfomance,
)


class EnrollmentInline(admin.StackedInline):
    model = Enrollment
    can_delete = False
    verbose_name_plural = "Enrollment"


class CustomUserAdmin(UserAdmin):
    inlines = (EnrollmentInline,)


# Unregister the original User admin and register the new one
# admin.site.unregister(CustomUser)
admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ["title", "slug"]
    prepopulated_fields = {"slug": ("title",)}


class ModuleInline(admin.StackedInline):
    model = Module


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["title", "subject", "created", "owner"]
    list_filter = ["created", "subject"]
    search_fields = ["title", "overview"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ModuleInline]


@admin.register(Rct)
class RctAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "facebook", "twitter", "linked_in")


@admin.register(Testimonials)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "date")
    list_filter = ("date",)


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ("module", "content_type", "object_id", "order")
    list_filter = ("module", "content_type")


@admin.register(Partners)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ("name", "website")
    search_fields = ("name",)


from django.contrib import admin
from .models import Enrollment, Perfomance, Module, OverallPerformance


class PerformanceInline(admin.TabularInline):
    model = Perfomance
    extra = 7
    fields = ("module", "score")

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj:
            # Get the courses related to the enrollment
            courses = obj.course.all()
            # Get modules related to the courses
            modules = Module.objects.filter(course__in=courses)
            formset.form.base_fields["module"].queryset = modules
        return formset


class OverallPerformanceInline(admin.StackedInline):
    model = OverallPerformance
    extra = 1
    fields = ("overall_score",)


class EnrollmentAdminForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ["student", "course", "certificate_issued"]
        widgets = {
            "course": forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter users to only those belonging to the 'students' group
        students_group = Group.objects.get(name="students")
        queryset = students_group.user_set.all()
        # Override label_from_instance to customize how User objects are displayed
        self.fields["student"].label_from_instance = self.label_from_user_instance
        self.fields["student"].queryset = queryset

    def label_from_user_instance(self, obj):
        # Customize how each User instance is displayed in the form field
        return f"{obj.username} - {obj.get_full_name()}"


class EnrollmentAdmin(admin.ModelAdmin):
    form = EnrollmentAdminForm

    def student_full_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"

    student_full_name.short_description = "Student Name"

    def display_courses(self, obj):
        return ", ".join([course.title for course in obj.course.all()])

    def student_username(self, obj):
        return obj.student.username

    student_username.short_description = "Username"

    display_courses.short_description = "Courses Enrolled"

    list_display = (
        "student_username",
        "student_full_name",
        "enrollment_date",
        "certificate_issued",
        "display_courses",
    )
    list_filter = ("certificate_issued", "enrollment_date", "course")
    search_fields = (
        "student__username",
        "course__title",
        "student__first_name",
        "student__last_name",
    )
    inlines = [PerformanceInline, OverallPerformanceInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Exclude enrollments that already have results
        return qs.filter(results__isnull=True)

    def save_model(self, request, obj, form, change):
        # Save the enrollment object
        super().save_model(request, obj, form, change)

        # Update the courses associated with this enrollment
        courses = form.cleaned_data.get("course", [])
        obj.course.set(courses)


admin.site.register(Enrollment, EnrollmentAdmin)
admin.site.register(Module)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "amount", "payment_date")
    list_filter = ("payment_date", "amount")
    search_fields = ("enrollment__student__username", "enrollment__course__title")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "question")


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("question", "answer")


from django.contrib import admin
from .models import Perfomance, Enrollment, Module


class PerformanceAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "module", "score")
    list_filter = ("module", "enrollment")
    search_fields = ("enrollment__student__username", "module__title")


admin.site.register(Perfomance, PerformanceAdmin)


@admin.register(OverallPerformance)
class OverallPerformanceAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "overall_score")
    search_fields = ("enrollment",)
