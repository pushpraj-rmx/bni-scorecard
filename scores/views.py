from django.shortcuts import render, redirect
import pandas as pd
from .models import EmployeeScore
from .forms import UploadFileForm
from django.contrib import messages

def upload_file(request):
    if request.method == 'POST':
        if 'preview' in request.POST:
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                file = request.FILES['file']
                file_extension = file.name.split('.')[-1]

                try:
                    if file_extension in ['xls', 'xlsx']:
                        df = pd.read_excel(file, engine='openpyxl' if file_extension == 'xlsx' else None)
                    elif file_extension == 'ods':
                        df = pd.read_excel(file, engine='odf')
                    elif file_extension == 'csv':
                        df = pd.read_csv(file)
                    else:
                        messages.error(request, 'Unsupported file type')
                        return redirect('upload_file')
                except Exception as e:
                    messages.error(request, f'Error reading file: {e}')
                    return redirect('upload_file')

                df.columns = [col.replace(' ', '_') for col in df.columns]  # Replace spaces with underscores

                request.session['df'] = df.to_dict(orient='records')
                context = {
                    'data': df.to_dict(orient='records'),
                    'form': form,
                    'preview': True
                }
                return render(request, 'scores/upload_file.html', context)
        elif 'confirm' in request.POST:
            df = pd.DataFrame(request.session.get('df'))
            for index, row in df.iterrows():
                EmployeeScore.objects.create(
                    name=row['Name'],
                    absent_value=row['Absent_Value'],
                    late_value=row['Late_Value'],
                    referral_value=row['Referral_Value'],
                    visitors_value=row['Visitors_Value'],
                    tyfcb_value=row['TYFCB_Value'],
                    testimonial_value=row['Testimonial_Value'],
                    training_value=row['Training_Value']
                )
            messages.success(request, 'Data imported successfully')
            return redirect('employee_scores')
    else:
        form = UploadFileForm()
    return render(request, 'scores/upload_file.html', {'form': form})



def get_score_class(score):
    if score < 10:
        return 'score-low'
    elif 10 <= score < 20:
        return 'score-medium'
    elif 20 <= score < 30:
        return 'score-high'
    else:
        return 'score-very-high'



def calculate_scores(employee):
    # Calculate Absent Score
    if employee.absent_value == 0:
        absent_score = 15
    elif employee.absent_value == 1:
        absent_score = 10
    elif employee.absent_value == 2:
        absent_score = 5
    else:
        absent_score = 0

    # Calculate Late Score
    if employee.late_value == 0:
        late_score = 5
    else:
        late_score = 0

    # Calculate Referral Score
    if employee.referral_value >= 32:
        referral_score = 20
    elif 26 <= employee.referral_value <= 31:
        referral_score = 15
    elif 20 <= employee.referral_value <= 25:
        referral_score = 10
    elif 13 <= employee.referral_value <= 19:
        referral_score = 5
    else:
        referral_score = 0

    # Calculate Visitors Score
    if employee.visitors_value >= 20:
        visitors_score = 20
    elif 13 <= employee.visitors_value <= 19:
        visitors_score = 15
    elif 7 <= employee.visitors_value <= 12:
        visitors_score = 10
    elif 3 <= employee.visitors_value <= 6:
        visitors_score = 5
    else:
        visitors_score = 0

    # Calculate TYFCB Score
    if employee.tyfcb_value >= 2000000:
        tyfcb_score = 15
    elif 1000000 <= employee.tyfcb_value < 2000000:
        tyfcb_score = 10
    elif 500000 <= employee.tyfcb_value < 1000000:
        tyfcb_score = 5
    else:
        tyfcb_score = 0

    # Calculate Training Score
    if employee.training_value >= 3:
        training_score = 15
    elif employee.training_value == 2:
        training_score = 10
    elif employee.training_value == 1:
        training_score = 5
    else:
        training_score = 0

    # Calculate Testimonial Score
    if employee.testimonial_value >= 2:
        testimonial_score = 10
    elif employee.testimonial_value == 1:
        testimonial_score = 5
    else:
        testimonial_score = 0

    # Calculate Projected Score
    projected_score = (absent_score + late_score + referral_score +
                       visitors_score + tyfcb_score + training_score +
                       testimonial_score)
    
    
    
    scores = {
        'name': employee.name,
        'absent_score': absent_score,
        'late_score': late_score,
        'referral_score': referral_score,
        'visitors_score': visitors_score,
        'tyfcb_score': tyfcb_score,
        'training_score': training_score,
        'testimonial_score': testimonial_score,
        'projected_score': projected_score
    }
    
    score_classes = {k + '_class': get_score_class(v) for k, v in scores.items() if k.endswith('_score')}
    scores.update(score_classes)
    
    return scores



    # return {
    #     'name': employee.name,
    #     'absent_score': absent_score,
    #     'late_score': late_score,
    #     'referral_score': referral_score,
    #     'visitors_score': visitors_score,
    #     'tyfcb_score': tyfcb_score,
    #     'training_score': training_score,
    #     'testimonial_score': testimonial_score,
    #     'projected_score': projected_score
    # }



def employee_scores(request):
    employees = EmployeeScore.objects.all()
    results = [calculate_scores(employee) for employee in employees]
    return render(request, 'scores/employee_scores.html', {'results': results})
  



def homepage(request):
    return render(request, 'scores/homepage.html')