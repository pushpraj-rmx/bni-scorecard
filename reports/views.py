import pandas as pd
from django.shortcuts import render, redirect
from .forms import UploadFilesForm
from .models import EmployeeScore, MemberTrainingReport
import mimetypes


def home(request):
    return render(request, 'reports/home.html')


def upload_files(request):
    if request.method == 'POST':
        scores_file = request.FILES['scores_file']
        training_file = request.FILES['training_file']
        process_files(scores_file, training_file)
        return redirect('upload_files')
    return render(request, 'reports/upload.html')

def process_files(scores_file, training_file):
    # Clear existing data
    EmployeeScore.objects.all().delete()
    MemberTrainingReport.objects.all().delete()

    # Determine the correct engine based on file type
    def get_engine(file):
        file_type = mimetypes.guess_type(file.name)[0]
        if file_type in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel.sheet.macroEnabled.12']:
            return 'openpyxl'
        elif file_type == 'application/vnd.ms-excel':
            return 'xlrd'
        elif file_type == 'application/vnd.oasis.opendocument.spreadsheet':
            return 'odf'
        else:
            raise ValueError("Unsupported file type: {}".format(file_type))

    scores_engine = get_engine(scores_file)
    training_engine = get_engine(training_file)

    # Process scores file
    scores_df = pd.read_excel(scores_file, engine=scores_engine)
    for _, row in scores_df.iterrows():
        EmployeeScore.objects.create(
            name=row['Name'],
            absent_value=row['Absent'],
            late_value=row['Late'],
            referral_value=row['Referrals'],
            visitors_value=row['Visitors'],
            TYFCB_value=row['TYFCB'],
            training_value=row['Training'],
            testimonial_value=row['Testimonials']
        )

    # Process training file
    training_df = pd.read_excel(training_file, engine=training_engine)
    for _, row in training_df.iterrows():
        MemberTrainingReport.objects.create(
            member_name=row['MemberName'],
            training_attended=row['TrainingAttended']
        )

def employee_scores(request):
    employees = EmployeeScore.objects.all()
    scores_data = [calculate_scores(employee) for employee in employees]
    return render(request, 'reports/employee_scores.html', {'scores_data': scores_data})

def calculate_scores(employee):
    return {
        'name': employee.name,
        'absent_score': 100 - employee.absent_value,
        'late_score': 100 - employee.late_value,
        'referral_score': employee.referral_value * 10,
        'visitors_score': employee.visitors_value * 10,
        'TYFCB_score': employee.TYFCB_value * 10,
        'training_score': employee.training_value * 10,
        'testimonial_score': employee.testimonial_value * 10,
    }
