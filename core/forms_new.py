from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User, Teacher, Student, Position, Candidate, Broadcast, ElectionSettings

CLASS_CHOICES = [
    ('', 'Select Class'),
    ('9th', '9th'),
    ('10th', '10th'),
    ('11th', '11th'),
    ('12th', '12th'),
]

SECTION_CHOICES = [
    ('', 'Select Section'),
    ('A', 'A'),
    ('B', 'B'),
    ('C', 'C'),
    ('D', 'D'),
]

class PrincipalLoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_principal() and not user.is_superuser:
            raise forms.ValidationError("This login is restricted to Principals only.")
        super().confirm_login_allowed(user)

class TeacherLoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_teacher():
            raise forms.ValidationError("This login is restricted to Teachers only.")
        super().confirm_login_allowed(user)

class StudentLoginForm(forms.Form):
    aadhaar = forms.CharField(max_length=12, label="Aadhaar Number")
    phone = forms.CharField(max_length=15, label="Phone Number", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        aadhaar = cleaned_data.get("aadhaar")
        phone = cleaned_data.get("phone")

        if aadhaar and phone:
            try:
                student = Student.objects.get(aadhaar=aadhaar)
                user = student.user
                if not user.check_password(phone):
                     raise forms.ValidationError("Invalid Aadhaar number or Phone number.")
                self.user_cache = user
            except Student.DoesNotExist:
                raise forms.ValidationError("Invalid Aadhaar number or Phone number.")
        return cleaned_data

    def get_user(self):
        return self.user_cache

class TeacherCreationForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    phone = forms.CharField(max_length=15)
    class_in_charge = forms.ChoiceField(choices=CLASS_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    section_in_charge = forms.ChoiceField(choices=SECTION_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Teacher
        fields = ['class_in_charge', 'section_in_charge']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with this username already exists.")
        return username

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['username'], 
            role='teacher',
            phone=self.cleaned_data['phone']
        )
        teacher = super().save(commit=False)
        teacher.user = user
        if commit:
            teacher.save()
        return teacher

class StudentCreationForm(forms.ModelForm):
    aadhaar = forms.CharField(max_length=12)
    phone = forms.CharField(max_length=15)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    class_name = forms.ChoiceField(choices=CLASS_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    section = forms.ChoiceField(choices=SECTION_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Student
        fields = ['aadhaar', 'class_name', 'section']

    def __init__(self, *args, **kwargs):
        self.teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        if self.teacher:
            self.fields['class_name'].initial = self.teacher.class_in_charge
            self.fields['class_name'].disabled = True
            self.fields['section'].initial = self.teacher.section_in_charge
            self.fields['section'].disabled = True

    def clean_aadhaar(self):
        aadhaar = self.cleaned_data.get('aadhaar')
        if User.objects.filter(username=aadhaar).exists():
            raise forms.ValidationError("A student with this Aadhaar already exists.")
        return aadhaar

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['aadhaar'],
            password=self.cleaned_data['phone'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            role='student',
            phone=self.cleaned_data['phone']
        )
        student = super().save(commit=False)
        student.user = user
        student.aadhaar = self.cleaned_data['aadhaar']
        if self.teacher:
            student.class_name = self.teacher.class_in_charge
            student.section = self.teacher.section_in_charge
        if commit:
            student.save()
        return student

class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['name']

class CandidateNominationForm(forms.ModelForm):
    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        label="Select Student",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Candidate
        fields = ['student', 'position', 'manifesto', 'photo']
        widgets = {
            'position': forms.Select(attrs={'class': 'form-select'})
        }

class BroadcastForm(forms.ModelForm):
    class Meta:
        model = Broadcast
        fields = ['title', 'message', 'attachment', 'is_pinned']

class ElectionSettingsForm(forms.ModelForm):
    start_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    end_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    publish_results = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta:
        model = ElectionSettings
        fields = ['start_time', 'end_time', 'publish_results']

class PrincipalCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    phone = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = 'principal'
        user.phone = self.cleaned_data.get('phone', '')
        if commit:
            user.save()
        return user
