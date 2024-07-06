from django.contrib import admin
from django import forms
from django.contrib.auth.models import Group
from .models import Course, Enrollment, User
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
)


class EnrollmentInline(admin.StackedInline):
    model = Enrollment
    can_delete = False
    verbose_name_plural = "Enrollment"


class CustomUserAdmin(UserAdmin):
    inlines = (EnrollmentInline,)


# Unregister the original User admin and register the new one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# Unregister the original User admin and register the new one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


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


# @admin.register(Text)
# class TextAdmin(admin.ModelAdmin):
#     # list_display = ('title', 'owner', 'created')
#     pass
# @admin.register(File)
# class FileAdmin(admin.ModelAdmin):
#     # list_display = ('title', 'owner', 'created')
#      pass
# @admin.register(Image)
# class ImageAdmin(admin.ModelAdmin):
#     # list_display = ('title', 'owner', 'created')
#      pass
# @admin.register(Video)
# class VideoAdmin(admin.ModelAdmin):
#     # list_display = ('title', 'owner', 'created')
#      pass


@admin.register(Partners)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ("name", "website")
    search_fields = ("name",)


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
    list_display = (
        "student",
        "enrollment_date",
        "certificate_issued",
    )
    list_filter = ("certificate_issued", "enrollment_date", "course")
    search_fields = ("student__username", "course__title")

    def display_courses(self, obj):
        return ", ".join([course.title for course in obj.courses.all()])

    display_courses.short_description = "Courses Enrolled"

    def save_model(self, request, obj, form, change):
        # Save the enrollment object
        super().save_model(request, obj, form, change)

        # Update the courses associated with this enrollment
        courses = form.cleaned_data.get("course", [])
        obj.course.set(courses)


admin.site.register(Enrollment, EnrollmentAdmin)


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
