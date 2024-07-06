from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .fields import OrderField
from django.template.loader import render_to_string


class Subject(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Course(models.Model):
    owner = models.ForeignKey(
        User, related_name="courses_created", on_delete=models.CASCADE
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
        User, related_name="%(class)s_related", on_delete=models.CASCADE
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
        User, related_name="enrollments", on_delete=models.CASCADE
    )
    course = models.ManyToManyField(Course, related_name="enrollments")
    enrollment_date = models.DateField()
    finishing_date = models.DateTimeField(blank=True, null=True)
    certificate_issued = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.username} enrolled in {', '.join(course.title for course in self.course.all())}"


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
