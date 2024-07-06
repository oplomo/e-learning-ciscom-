from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.views import LoginView
from django.views.generic.list import ListView
from django.contrib.auth.hashers import make_password
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from .forms import Moduleformset, Admission_form, PaymentForm, ContactForm
from django.views.generic.base import TemplateResponseMixin, View
from django.forms.models import modelform_factory
from django.apps import apps
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.db.models import Count, Sum
from django.views.generic.detail import DetailView
from django.contrib.auth.decorators import login_required
from .models import (
    Module,
    Content,

    Testimonials,
    Course,
    Rct,
    Subject,
    Enrollment,
    Payment,
    User,
    Question,
    Answer,
    Partners,
)
from decimal import Decimal
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import F, ExpressionWrapper, DecimalField, Q, Case, When
import random
from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa
from urllib.parse import quote
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test



def group_required(group_name):
    def decorator(view_func):
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_superuser or request.user.groups.filter(name=group_name).exists():
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied
        return _wrapped_view
    return decorator


def permission_denied_view(request, exception=None):
    return render(request, '403.html', status=403)


def handle_message(request=None, **kwargs):
    global inquiry
    if request.method == "POST":
        inquiry = ContactForm(data=request.POST)
        if inquiry.is_valid():
            name = inquiry.cleaned_data["name"]
            from_email = inquiry.cleaned_data["email"]
            subject = inquiry.cleaned_data["subject"]
            message = f"{inquiry.cleaned_data["message"]}\n [this messages has been sent  by {name}- {from_email}]"
            send_mail(
                subject,
                message,
                from_email,
                [settings.EMAIL_HOST_USER],                
                fail_silently=False,
            )

            messages.success(request, "Email has been sent successfully.")
            inquiry = ContactForm()
        else:
            messages.error(request, "There was an error with your submission.")
            inquiry  = ContactForm()
    else:
        inquiry = ContactForm()

def home_page(request):
    rct = get_object_or_404(Rct, pk=1)
    # courses = Course.objects.all()[:8]
    subject = Subject.objects.all()
    testimonials = Testimonials.objects.all()

    all_careers = list(Course.objects.all())
    random.shuffle(all_careers)
    careers = all_careers[:8]
    context = {
        "rct": rct,
        "course": careers,
        "subject": subject,
        "testimonial": testimonials,
        "more_links": [
            {"title": "Link 1", "url": "#link1"},
            {"title": "Link 2", "url": "#link2"},
            {"title": "Link 3", "url": "#link3"},
        ],
    }

    return render(request, "public/home.html", context)


def home_courses(request, id=None):
    if id:
        courses = Course.objects.filter(subject=id)
        filtered_by = get_object_or_404(Subject, pk=id)
    else:
        courses = Course.objects.all()
        filtered_by = None
    sub = Subject.objects.all()
    context = {
        "courses": courses,
        "sub": sub,
        "filter": filtered_by,
    }
    return render(request, "public/our_courses.html", context)


def course_about(request, id, name):
    course = get_object_or_404(Course, pk=id, title=name)
    rct = get_object_or_404(Rct, pk=1)
    handle_message(request)
    context = {
        "form":inquiry,
        "course": course,
        "rct": rct,
    }
    return render(request, "public/course_about.html", context)


def subscription(request):
    subs = Course.objects.all()
    context = {
        "subs": subs,
    }
    return render(request, "public/subscription.html", context)


def partners(request):
    partners = Partners.objects.all()
    context = {"pat": partners}
    return render(request, "public/partners.html", context)


def faqs(request):
    question = Question.objects.all()
    answer = Answer.objects.all()
    context = {
        "q": question,
        "a": answer,
    }
    return render(request, "public/faqs.html", context)


def about(request):
    return render(request, "public/about.html")


def contacts(request):
    rct = get_object_or_404(Rct, pk=1)
    handle_message(request)

    context = {
        "form": inquiry,
        "rct": rct,
    }
    return render(request, "public/contacts.html", context)

def terms(request):
    rct = get_object_or_404(Rct, pk=1)
    context = {
        "rct": rct,
    }
    return render(request,"public/terms.html",context)
 
def privacy(request):
    rct = get_object_or_404(Rct, pk=1)
    context = {

        "rct": rct,
    }
    return render(request,"public/privacy.html",context)

def Instractor_portal(request):
    return render(request, "instractor/instractor_dashboard.html")


@group_required('students')
def Student_dashboard(request):
    return render(request, "student/student_dashboard.html")


class CustomLoginView(LoginView):
    def get_success_url(self):
        user = self.request.user

        if user.groups.filter(name="instractor").exists():

            return reverse_lazy("manage_course_list")
        else:
            return reverse_lazy("student_dashboard")


class OwnerMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin:
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerCoursemixin(OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin):
    model = Course
    fields = [
        "subject",
        "title",
        "overview",
        "image",
        "fee",
        "cert_benefit",
        "period_in_weeks",
    ]
    success_url = reverse_lazy("manage_course_list")


class OwnerCourseEditmixin(OwnerCoursemixin, OwnerEditMixin):
    template_name = "courses/manage/course/form.html"


class ManageCourseListView(OwnerCoursemixin, ListView):
    template_name = "courses/manage/course/list.html"
    permission_required = "courses.view_course"
    raise_exception = True  


class CourseCreateView(OwnerCourseEditmixin, CreateView):
    permission_required = "courses.add_course"
    raise_exception = True  


class CourseUpdateView(OwnerCourseEditmixin, UpdateView):
    permission_required = "courses.change_course"


class CourseDeleteView(OwnerCoursemixin, DeleteView):
    template_name = "courses/manage/course/delete.html"
    permission_required = "courses.delete_course"


class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = "courses/manage/module/formset.html"
    course = None

    def get_formset(self, data=None):
        return Moduleformset(instance=self.course, data=data)

    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course, id=pk, owner=request.user)
        return super().dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({"course": self.course, "formset": formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect("manage_course_list")
        return self.render_to_response({"course": self.course, "formset": formset})


class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = "courses/manage/content/form.html"

    def get_model(self, model_name):
        if model_name in ["text", "video", "image", "file"]:
            return apps.get_model(app_label="courses", model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(
            model, exclude=["owner", "order", "created", "updated"]
        )
        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(
            Module, id=module_id, course__owner=request.user
        )
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model, id=id, owner=request.user)
        return super().dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({"form": form, "object": self.obj})

    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(
            self.model, instance=self.obj, data=request.POST, files=request.FILES
        )
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # new content
                Content.objects.create(module=self.module, item=obj)
            return redirect("module_content_list", self.module.id)
        return self.render_to_response({"form": form, "object": self.obj})


class ContentDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(Content, id=id, module__course__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect("module_content_list", module.id)


class ModuleContentListView(TemplateResponseMixin, View):
    template_name = "courses/manage/module/content_list.html"

    def get(self, request, module_id):
        module = get_object_or_404(Module, id=module_id, course__owner=request.user)
        return self.render_to_response({"module": module})


class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id, course__owner=request.user).update(order=order)
        return self.render_json_response({"saved": "OK"})


class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id, module__course__owner=request.user).update(
                order=order
            )
        return self.render_json_response({"saved": "OK"})


class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name = "courses/course/list.html"

    def get(self, request, subject=None):
        subjects = Subject.objects.annotate(total_courses=Count("courses"))
        courses = Course.objects.annotate(total_modules=Count("modules"))
        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            courses = courses.filter(subject=subject)
        return self.render_to_response(
            {"subjects": subjects, "subject": subject, "courses": courses}
        )


class CourseDetailView(DetailView):
    model = Course
    template_name = "courses/course/detail.html"

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["enroll_form"] = CourseEnrollForm(initial={"course": self.object})
    #     return context


# class StudentEnrollCourseView(LoginRequiredMixin, FormView):
#     course = None
#     form_class = CourseEnrollForm

#     def form_valid(self, form):
#         self.course = form.cleaned_data["course"]
#         self.course.enrollment.add(self.request.user)
#         return super().form_valid(form)

#     def get_success_url(self):
#         return reverse_lazy("student_course_detail", args=[self.course.id])


class StudentCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = "student/course/list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(enrollments__student=self.request.user)

class StudentCourseDetailView(DetailView):
    model = Course
    template_name = "student/course/detail.html"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(enrollments__student=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get course object
        course = self.get_object()
        if "module_id" in self.kwargs:
            # get current module
            context["module"] = course.modules.get(id=self.kwargs["module_id"])
        else:
            # get first module if it exists
            modules = course.modules.all()
            if modules.exists():
                context["module"] = modules[0]
            else:
                context["module"] = None
        return context

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    # Get the group 'students'
    students_group = Group.objects.get(name="students")

    # Get all users in the 'students' group
    students = User.objects.filter(groups=students_group)

    # Prefetch enrollments and related objects to minimize database hits
    students = students.prefetch_related("enrollments__course", "enrollments__payments")

    # Initialize filter parameters
    num_courses_filter = request.POST.get("num_courses_filter")
    exact_num_courses_filter = request.POST.get("exact_num_courses_filter")
    certificate_issued_filter = request.POST.get("certificate_issued_filter")
    course_filter = request.POST.get("course_filter")
    start_date_filter = request.POST.get("start_date_filter")  # Start date filter
    end_date_filter = request.POST.get("end_date_filter")  # End date filter
    fee_balance_filter = request.POST.get("fee_balance_filter")  # Fee balance filter

    # Apply filters based on POST data
    if num_courses_filter:
        students = students.annotate(
            num_courses=Count("enrollments__course", distinct=True)
        ).filter(num_courses__gt=num_courses_filter)

    if exact_num_courses_filter:
        students = students.annotate(
            num_courses=Count("enrollments__course", distinct=True)
        ).filter(num_courses=exact_num_courses_filter)

    if certificate_issued_filter:
        students = students.filter(enrollments__certificate_issued=True)

    if course_filter:
        students = students.filter(enrollments__course__title__icontains=course_filter)

    if start_date_filter and end_date_filter:
        start_date = datetime.strptime(start_date_filter, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_filter, "%Y-%m-%d").date()
        students = students.filter(
            enrollments__enrollment_date__range=(start_date, end_date)
        )

    student_data = []

    for student in students:
        total_amount = 0
        total_paid = 0
        fee_balance = 0

        # Calculate total amount and total paid
        if hasattr(student, "enrollments"):
            enrollment = student.enrollments
            courses = enrollment.course.all()
            payments = enrollment.payments.all()

            # Calculate total amount for courses
            total_amount = sum(course.fee or 0 for course in courses)

            # Calculate total paid from payments
            total_paid = sum(payment.amount for payment in payments)

            # Calculate fee balance
            fee_balance = total_amount - total_paid

        # Apply fee balance filter
        if fee_balance_filter:
            fee_balance_filter = Decimal(
                fee_balance_filter
            )  # Convert to Decimal if necessary
            if fee_balance < fee_balance_filter:
                continue  # Skip this student if fee balance is less than the filter

        student_data.append(
            {
                "student": student,
                "total_amount": total_amount,
                "total_paid": total_paid,
                "fee_balance": fee_balance,
            }
        )

    # Fetch all unique course titles for filtering
    courses = Course.objects.values_list("title", flat=True).distinct()

    context = {
        "student_data": student_data,
        "courses": courses,  # Provide course titles for the dropdown
    }
    return render(request, "admin/student_register.html", context)


def student_register_pdf(request):
    students_group = Group.objects.get(name="students")
    students = User.objects.filter(groups=students_group)
    students = students.prefetch_related("enrollments__course", "enrollments__payments")

    num_courses_filter = request.GET.get("num_courses_filter")
    exact_num_courses_filter = request.GET.get("exact_num_courses_filter")
    certificate_issued_filter = request.GET.get("certificate_issued_filter")
    course_filter = request.GET.get("course_filter")
    start_date_filter = request.GET.get("start_date_filter")
    end_date_filter = request.GET.get("end_date_filter")
    fee_balance_filter = request.GET.get("fee_balance_filter")

    # Filter students based on the provided filters
    if num_courses_filter:
        students = students.annotate(
            num_courses=Count("enrollments__course", distinct=True)
        ).filter(num_courses__gt=num_courses_filter)

    if exact_num_courses_filter:
        students = students.annotate(
            num_courses=Count("enrollments__course", distinct=True)
        ).filter(num_courses=exact_num_courses_filter)

    if certificate_issued_filter:
        students = students.filter(enrollments__certificate_issued=True)

    if course_filter:
        students = students.filter(enrollments__course__title__icontains=course_filter)

    if start_date_filter and end_date_filter:
        start_date = datetime.strptime(start_date_filter, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_filter, "%Y-%m-%d").date()
        students = students.filter(
            enrollments__enrollment_date__range=(start_date, end_date)
        )

    student_data = []

    for student in students:
        total_amount = 0
        total_paid = 0
        fee_balance = 0

        if hasattr(student, "enrollments"):
            enrollment = student.enrollments
            courses = enrollment.course.all()
            payments = enrollment.payments.all()

            total_amount = sum(course.fee or 0 for course in courses)
            total_paid = sum(payment.amount for payment in payments)
            fee_balance = total_amount - total_paid

        if fee_balance_filter:
            fee_balance_filter = Decimal(fee_balance_filter)
            if fee_balance < fee_balance_filter:
                continue

        student_data.append(
            {
                "student": student,
                "total_amount": total_amount,
                "total_paid": total_paid,
                "fee_balance": fee_balance,
            }
        )

    courses = Course.objects.values_list("title", flat=True).distinct()

    context = {
        "student_data": student_data,
        "courses": courses,
    }

    # Generate the HTML for PDF conversion
    html = render_to_string("admin/student_register_pdf.html", context)

    # Construct the file name based on filters
    filter_parts = []
    if num_courses_filter:
        filter_parts.append(f"num_courses_gt_{num_courses_filter}")
    if exact_num_courses_filter:
        filter_parts.append(f"exact_num_courses_{exact_num_courses_filter}")
    if certificate_issued_filter:
        filter_parts.append("certificate_issued")
    if course_filter:
        filter_parts.append(f"course_{course_filter.replace(' ', '_')}")
    if start_date_filter:
        filter_parts.append(f"from_{start_date_filter}")
    if end_date_filter:
        filter_parts.append(f"to_{end_date_filter}")
    if fee_balance_filter:
        filter_parts.append(f"fee_balance_gt_{fee_balance_filter}")

    filter_str = "_".join(filter_parts) if filter_parts else "all"
    filename = f"student_register_{filter_str}.pdf"
    filename = quote(filename)  # Ensure the filename is URL-safe

    # Generate the PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    pisa_status = pisa.CreatePDF(html, dest=response, encoding="UTF-8")

    if pisa_status.err:
        return HttpResponse("We had some errors <pre>" + html + "</pre>")
    return response


def student_admision(request):
    school = get_object_or_404(Rct, pk=1)
    courses = Course.objects.all()
    if request.method == "POST":
        form = Admission_form(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]
            course = form.cleaned_data["course"]

            certificate_issued = form.cleaned_data["certificate_issued"]

            course_ids = request.POST.getlist(
                "course"
            )  

        
            password = username
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "password": make_password(password),  # Hashed password
                },
            )

            group_students, created = Group.objects.get_or_create(name="students")
            user.groups.add(group_students)

            selected_courses = Course.objects.filter(id__in=course_ids)

            enrollment = Enrollment.objects.create(
                student=user,
                certificate_issued=certificate_issued,
            )
            enrollment.course.add(*selected_courses)

            enrolled_courses = ", ".join(
                [course.title for course in enrollment.course.all()]
            )
            subject = "successful enrollment"
            message = f"Dear {first_name},\n\nWe are thrilled to inform you that you have successfully registered at {school.name} and enrolled in the following courses:\n\n{enrolled_courses}.\n\nYour username is {username} and your password is {password}.\n\nPlease use this information to log in to your account and access your learning materials.\n\nWishing you the best of luck as you embark on your educational journey with us!"
            From = settings.EMAIL_HOST_USER
            TO = [email]
            
            if any(course.title.lower() == 'cisco certified network professional (ccnp)' for course in selected_courses) or any(course.title.lower() == 'cisco certified network associate (ccna)' for course in selected_courses):
                message += f"\nFor Cisco courses, international certification is offered as well as granted permision to learn on cisco website. For more information or inquiries, please contact the admin\n\n"
            
            message += "\n\nWarm regards,\nThe {school.name} Team"          
            
            send_mail(
                subject,
                message,
                From,
                TO,
                fail_silently=False,
            )

            # adm_subject = "New Student Enrollment"
            # adm_message = (
            #     f"A new student has enrolled. Username: {username}, Name: {first_name} {last_name}, Email: {email}",
            # )
            # adm_From = settings.EMAIL_HOST_USER
            # adm_to = [settings.ADMIN_EMAIL]
            # send_mail(
            #     adm_subject,
            #     adm_message,
            #     adm_From,
            #     adm_to,
            #     fail_silently=False,
            # )

            return redirect("admin_dashboard")
    else:
        form = Admission_form()
    return render(
        request, "admin/student_registration.html", {"form": form, "courses": courses}
    )


def student_info(request, student_id):
    student = get_object_or_404(User, pk=student_id)
    enrollments = Enrollment.objects.filter(student=student)
    payments = Payment.objects.filter(enrollment__in=enrollments)

    total_amount = sum(
        course.fee for enrollment in enrollments for course in enrollment.course.all()
    )
    total_paid = sum(payment.amount for payment in payments)
    total_balance = total_amount - total_paid

    context = {
        "student": student,
        "enrollments": enrollments,
        "payments": payments,
        "total_amount": total_amount,
        "total_paid": total_paid,
        "total_balance": total_balance,
    }
    return render(request, "admin/student_info.html", context)


def student_payment(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, pk=enrollment_id)
    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.enrollment = enrollment
            payment.save()
            return redirect(
                "student_info", student_id=enrollment.student.id
            )  # Redirect to student info
    else:
        form = PaymentForm()

    context = {
        "form": form,
        "enrollment": enrollment,
    }
    return render(request, "admin/student_payment.html", context)


def student_info_pdf(request, student_id):
    student = get_object_or_404(User, pk=student_id)
    enrollments = Enrollment.objects.filter(student=student)
    payments = Payment.objects.filter(enrollment__in=enrollments)

    total_amount = sum(
        course.fee for enrollment in enrollments for course in enrollment.course.all()
    )
    total_paid = sum(payment.amount for payment in payments)
    total_balance = total_amount - total_paid

    context = {
        "student": student,
        "enrollments": enrollments,
        "payments": payments,
        "total_amount": total_amount,
        "total_paid": total_paid,
        "total_balance": total_balance,
    }

    html = render_to_string("admin/student_info_pdf.html", context)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="student_info_{student_id}.pdf"'
    )

    pisa_status = pisa.CreatePDF(html, dest=response, encoding="UTF-8")

    if pisa_status.err:
        return HttpResponse("We had some errors <pre>" + html + "</pre>")
    return response


# def check_data(request):
#     co = get_object_or_404(Course, pk=1)

#     return render(request, "check_data.html", {"co": co})
