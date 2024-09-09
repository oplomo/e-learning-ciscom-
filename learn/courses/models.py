from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .fields import OrderField
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Sum
from decimal import Decimal


class Subject(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Course(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="courses_created",
        on_delete=models.CASCADE,
    )
    subject = models.ForeignKey(
        Subject, related_name="courses", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="images/course/photos", blank=True, null=True)
    cert_benefit = models.TextField(blank=True, null=True)
    international_certification = models.BooleanField(default=False)
    period_in_weeks = models.IntegerField(blank=True, null=True)
    fee = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.title

    def update_students_field(self):
        # Update the students field based on enrolled students
        student_ids = self.enrollments.values_list("student", flat=True).distinct()
        self.students.set(student_ids)


class Module(models.Model):
    course = models.ForeignKey(Course, related_name="modules", on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    order = OrderField(blank=True, for_fields=["course"], default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.order}.{self.title}"


class Content(models.Model):
    module = models.ForeignKey(
        Module, on_delete=models.CASCADE, related_name="contents"
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={"model__in": ("text", "video", "image", "file")},
    )
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey("content_type", "object_id")
    order = OrderField(blank=True, for_fields=["module"], default=0)

    class Meta:
        ordering = ["order"]


class ItemBase(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="%(class)s_related",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def render(self):
        return render_to_string(
            f"courses/content/{self._meta.model_name}.html", {"item": self}
        )


class Text(ItemBase):
    context = models.TextField()


class File(ItemBase):
    file = models.FileField(upload_to="files")


class Image(ItemBase):
    file = models.FileField(upload_to="images")


class Video(ItemBase):
    url = models.URLField()


class Rct(models.Model):
    name = models.CharField(max_length=50)
    motto = models.CharField(max_length=1000, blank=True, null=True)
    intro = models.TextField(blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    facebook = models.URLField(max_length=200, blank=True, null=True)
    twitter = models.URLField(max_length=200, blank=True, null=True)
    linked_in = models.URLField(max_length=200, blank=True, null=True)
    terms = models.TextField(blank=True, null=True)
    privacy = models.TextField(blank=True, null=True)
    outro = models.TextField(blank=True, null=True)
    adress = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)


class Partners(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    logo = models.ImageField(upload_to="images/partners", blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(
        upload_to="images/partners/buildings", blank=True, null=True
    )

    def __str__(self):
        return self.name


class Testimonials(models.Model):

    name = models.CharField(max_length=200)
    testimony = models.TextField()
    date = models.DateField(blank=True, null=True)


class Question(models.Model):
    question = models.TextField()

    def __str__(self):
        return self.question

    class meta:
        ordering = ["-id"]


class Answer(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answer"
    )
    answer = models.TextField()

    def __str__(self):
        return self.answer


class Enrollment(models.Model):
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name="enrollments", on_delete=models.CASCADE
    )
    course = models.ManyToManyField(Course, related_name="enrollments", blank=True)
    enrollment_date = models.DateField()
    finishing_date = models.DateField(blank=True, null=True)
    certificate_issued = models.BooleanField(default=False)
    overall_performance = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )

    def __str__(self):
        return f"{self.student.username},{self.student.first_name},{self.student.last_name} enrolled in {', '.join(course.title for course in self.course.all())}"


class Payment(models.Model):
    enrollment = models.ForeignKey(
        Enrollment, related_name="payments", on_delete=models.CASCADE
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()

    def __str__(self):
        return (
            f"{self.enrollment.student.username} - {self.amount} on {self.payment_date}"
        )


class Perfomance(models.Model):
    enrollment = models.ForeignKey(
        Enrollment, related_name="results", on_delete=models.CASCADE
    )
    module = models.ForeignKey(Module, related_name="results", on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Result for {self.enrollment.student.username} in {self.module.title}"

    class Meta:
        unique_together = ("enrollment", "module")

    @property
    def get_module_name(self):
        return self.module.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save the current score first

        # Calculate the total score for the enrollment
        total_score = self.enrollment.results.aggregate(
            total=Sum("score", default=Decimal(0))
        )["total"] or Decimal(0)

        # Ensure the overall performance record exists
        overall_performance, created = OverallPerformance.objects.get_or_create(
            enrollment=self.enrollment
        )

        # Update the overall score, providing a default of 0.00 if the total_score is None
        overall_performance.overall_score = (
            total_score if total_score is not None else Decimal("0.00")
        )
        overall_performance.save()


class OverallPerformance(models.Model):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE)
    overall_score = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00")
    )

    def get_average_score(self):
        # Calculate the number of module scores
        num_modules = self.enrollment.results.count()

        if num_modules == 0:
            return Decimal("0.00")

        # Calculate the average score
        average_score = self.overall_score / num_modules
        return average_score

    def get_status(self):
        average_score = self.get_average_score()

        if average_score >= 90:
            return "Excellent"
        elif 80 <= average_score < 90:
            return "Distinction"
        elif 70 <= average_score < 80:
            return "Credit"
        elif 60 <= average_score < 70:
            return "Pass"
        else:
            return "Fail"