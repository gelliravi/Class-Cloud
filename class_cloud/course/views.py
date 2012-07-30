#Don't think generic views are being used, might want to remove this
from django.views.generic import list_detail, date_based, TemplateView, RedirectView, DetailView
from django.views.generic.edit import FormView

#Models
from course.models import Course, Assignment, Grade, StudentGrade, SubmittedAssignment, Announcement, Discussion, Enrollment
from django.contrib.auth.models import User

#Model Forms
from course.models import CourseForm, AnnoucementForm, AssignmentForm, GradeForm
from django.forms.models import ModelForm, modelformset_factory

from django.shortcuts import render_to_response, RequestContext

from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.core.urlresolvers import reverse

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required

from django.template import defaultfilters

def calendar(request):
    assignment_list = []
    courses = []
    courses.extend(Course.objects.filter(students__username=request.user.username))
    
    for icourse in courses:
        course_assignments = Assignment.objects.filter(course=icourse)
        assignment_list.extend(course_assignments)

    return render_to_response('calendar.html',
    		{'assignments': assignment_list},
        	context_instance=RequestContext(request))


def passign(request):
    return render_to_response('passign.html',
        context_instance=RequestContext(request))


    


@login_required
@user_passes_test(lambda u: u.has_perm('course.student_view'))
def index(request):
    """ Template is passed a context
    
    The context is a dictionary mapping between template variable names and
    Python objects
    """
    courses = Course.objects.filter(students__username=request.user.username)
    return render_to_response('courses.html',
        {'courses': courses},
        context_instance=RequestContext(request))


@login_required
@user_passes_test(lambda u: u.has_perm('course.student_view'))
def courses(request, slug):
    courses = Course.objects.filter(students__username=request.user.username)
    return render_to_response('courses.html',
        {'courses': courses},
        context_instance=RequestContext(request))


def course_test(request, course_slug):
    
    selected_course = Course.objects.get(slug=course_slug)
    course_assignments = Assignment.objects.filter(course=selected_course)
    
    import pdb; pdb.set_trace()
    
    return HttpResponse(course_assignments)


@login_required
@user_passes_test(lambda u: u.has_perm('course.student_view'))
def wtf(request):
    student_grades = StudentGrade.objects.filter(student__username=request.user.username)
    return render_to_response('grades.html',
        {'student_grades': student_grades},
        context_instance=RequestContext(request))
    
@login_required
@user_passes_test(lambda u: u.has_perm('course.student_view'))
def course_grades(request, course_slug):    
    
    selected_course = Course.objects.get(slug=course_slug)
    
    # all grades associated with given course and user
    student_grades = StudentGrade.objects.filter(student__username=request.user.username,
                                          assignment__course=selected_course) 

    submitted = SubmittedAssignment.objects.filter(student__username=request.user.username)
    
    a_graded = []
    a_submitted = []
   
    for submission in submitted:
        for student_grade in student_grades:
            if submission.assignment == student_grade.assignment:
                a_graded.append((student_grade.grade, submission))
                                          
    #import pdb; pdb.set_trace()              
    template_name = 'course_grades.html'
    return render_to_response(template_name, 
        {'course':selected_course,
         'assignments_graded':a_graded,
         'grades':student_grades},
         context_instance=RequestContext (request))                                      

@login_required
@user_passes_test(lambda u: u.has_perm('course.student_view'))
def grades(request):
    
    #import pdb; pdb.set_trace()
    
    grades = {}
    
    #Filter student grades by the students enrolled courses
    enrolled = Enrollment.objects.filter(students__username=request.user.username)
    student_grades = StudentGrade.objects.filter(student__username=request.user.username)

    for grade in student_grades:
        if grade.assignment.course in [e.course for e in enrolled]:
            if grade.assignment.course.title not in grades:
                grades[grade.assignment.course.title] = [grade]
            else:
                grades[grade.assignment.course.title].append(grade)

    #import pdb; pdb.set_trace()

    return render_to_response('grades.html',
        {'student_grades': grades},
        context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda u: u.has_perm('course.student_view'))
def course(request, course_slug):
    selected_course = Course.objects.get(slug=course_slug)

    # Need to further filter this by due dates and wheather the assignment is active
    course_assignments = Assignment.objects.filter(course=selected_course)
    
    course_announcements = Announcement.objects.filter(course = selected_course)
    course_discussions = Discussion.objects.filter(course = selected_course)
    
    submitted = SubmittedAssignment.objects.filter(student__username=request.user.username)
    
    # all grades associated with given course and user
    student_grades = StudentGrade.objects.filter(student__username=request.user.username,
                                          assignment__course=selected_course)

    a_graded = []
    a_submitted = []
    a_uncomplete = []

    for submission in submitted:
        for student_grade in student_grades:
            if submission.assignment == student_grade.assignment:
                a_graded.append((student_grade.grade, submission))
        
    # Find submitted assignments that are not graded
    for submission in submitted:
        if submission.assignment not in [a[1].assignment for a in a_graded]:
            if submission.assignment.course == selected_course:
                a_submitted.append(submission)
    
    # Find assignments that have not been submitted
    for assignment in course_assignments:
        if assignment not in [i[1].assignment for i in a_graded]:
            if assignment not in [a.assignment for a in a_submitted]:
                a_uncomplete.append(assignment)
    
    template_name = 'course.html'
    return render_to_response(template_name, 
        {'course':selected_course,
         'assignments_graded':a_graded,
         'assignments_submitted':a_submitted,
         'assignments_inbox':a_uncomplete,
         'announcements':course_announcements,
         'discussions' :course_discussions,
         },
         context_instance=RequestContext(request))
    

@login_required
@user_passes_test(lambda u: u.has_perm('course.student_view'))
def assignments(request):

    assignment_list = []
    courses = []
    courses.extend(Course.objects.filter(students__username=request.user.username))
    
    for icourse in courses:
        course_assignments = Assignment.objects.filter(course=icourse)
        assignment_list.extend(course_assignments)
    
    return render_to_response('assignments.html',
        {'assignments': assignment_list},
        context_instance=RequestContext(request))
       
 
@login_required
@user_passes_test(lambda u: u.has_perm('course.student_view'))
def assignment(request, slug):

    a = Assignment.objects.get(slug=slug)
    return render_to_response('assignment.html',
        {'assignment':a},
        context_instance=RequestContext(request))


@login_required
@user_passes_test(lambda u: u.has_perm('course.student_view'))
def course_assignment(request, course_slug, assignment_slug):
    a = Assignment.objects.get(slug=assignment_slug)
    return render_to_response('assignment.html',
        {'assignment':a},
        context_instance=RequestContext(request))


def logout_view(request):
    logout(request)


@login_required
@user_passes_test(lambda u: u.has_perm('course.student_view'))
def announcements(request):

    announcement_list = []
    courses = []
    courses.extend(Course.objects.filter(students__username=request.user.username))
    
    for icourse in courses:
        course_announcements = Announcement.objects.filter(course=icourse)
        announcement_list.extend(course_announcements)
    
    return render_to_response('announcements.html',
        {'announcements': announcement_list},
        context_instance=RequestContext(request))


#we might not need this!!
def discussions(request):
	discussion_list = []
	courses = []
	courses.extend(Course.objects.filter(students__username=request.user.username))
	for icourse in courses:
		course_discussion = Announcement.objects.filter(course=icourse)
		discussion_list.extend(course_discussion)
		

## TEACHER VIEWS ##

@login_required
@user_passes_test(lambda u: u.has_perm('course.teacher_view'))
def teacher_index(request):
    courses = Course.objects.filter(teacher=request.user)
    teacher = request.user.get_full_name()
    #import pdb; pdb.set_trace()
    return render_to_response('teacher/index.html',
        {'teacher': teacher,
         'courses': courses },
        context_instance=RequestContext(request))


@login_required
@user_passes_test(lambda u: u.has_perm('course.teacher_view'))
def teacher_course(request, course_slug):
    
    course = Course.objects.get(slug=course_slug)

    return render_to_response('teacher/course.html',
        { 'course': course, },
        context_instance=RequestContext(request))


@login_required
@user_passes_test(lambda u: u.has_perm('course.teacher_view'))
def annoucement_add(request, course_slug):
    course = Course.objects.get(slug=course_slug)
    annoucement = Announcement(course=course, teacher=course.teacher)
    
    if request.method == 'POST':
        form = AnnoucementForm(request.POST, instance=annoucement)
        if form.is_valid():
            annoucement = form.save()
            return HttpResponseRedirect("/teacher/{0}/annoucement_complete/".format(course.slug))
    else:
        form = AnnoucementForm()
    
    return render_to_response('teacher/annoucement_add.html',
        { 'announcementForm': form },
        context_instance=RequestContext(request))


@login_required
@user_passes_test(lambda u: u.has_perm('course.teacher_view'))
def annoucement_complete(request, course_slug):
    return render_to_response('teacher/annoucement_complete.html',
        {'slug':course_slug},
        context_instance=RequestContext(request))


@login_required
@user_passes_test(lambda u: u.has_perm('course.teacher_view'))
def assignment_add(request, course_slug):
    course = Course.objects.get(slug=course_slug)
    assignment = Assignment(course=course, teacher=course.teacher)
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, instance=assignment)
        if form.is_valid():
            assignment = form.save()
            return HttpResponseRedirect("/teacher/{0}/assignment_complete/".format(course.slug))
    else:
        form = AssignmentForm()
    
    return render_to_response('teacher/assignment_add.html',
        { 'assignmentForm': form },
        context_instance=RequestContext(request))
        

@login_required
@user_passes_test(lambda u: u.has_perm('course.teacher_view'))
def assignment_complete(request, course_slug):
    return render_to_response('teacher/assignment_complete.html',
        {'slug':course_slug},
        context_instance=RequestContext(request))


@login_required
@user_passes_test(lambda u: u.has_perm('course.teacher_view'))
def grade_assignments(request, course_slug):

    course = Course.objects.get(slug=course_slug)

    course_assignments = Assignment.objects.filter(course=course)

    submitted = SubmittedAssignment.objects.filter(assignment__course=course)

    assignments = {}

    for assignment in course_assignments:
        assignments[assignment.name] = []
        for submission in submitted:
            if submission.assignment.name == assignment.name:
                assignments[assignment.name].append(submission)
                #submitted.remove(submission) #This will speed things up a little?

    return render_to_response('teacher/grade_assignments.html',
        {'assignments': assignments },
        context_instance=RequestContext(request))


@login_required
@user_passes_test(lambda u: u.has_perm('course.teacher_view'))
def grade_assignment(request, course_slug, assignment_slug, student_username):

    #student & assignment
    assignment = Assignment.objects.get(slug=assignment_slug)
    student = User.objects.get(username=student_username)
    
    grade = Grade()
    student_grade = StudentGrade(student=student, assignment=assignment)

    #GradeForm
    #StudentGradeForm

    #course = Course.objects.get(slug=course_slug)
    #assignment = Assignment(course=course, teacher=course.teacher)
    
    if request.method == 'POST':
        form = GradeForm(request.POST, request.FILES, instance=grade)
        if form.is_valid():
            grade = form.save()
            student_grade.grade = grade
            student_grade.save()
            return HttpResponseRedirect("/teacher/{0}/grade_assignments/{1}/{2}/assignment_graded/".format(course_slug, assignment_slug, student_username))
    else:
        form = GradeForm()


    return render_to_response('teacher/grade_assignment.html',
        {'form': form},
        context_instance=RequestContext(request))
    
    
@login_required
@user_passes_test(lambda u: u.has_perm('course.teacher_view'))
def grade_assignment_complete(request, course_slug, assignment_slug, student_username):
    return render_to_response('teacher/grade_assignment_complete.html',
        {'slug': course_slug},
        context_instance=RequestContext(request))

@login_required
@user_passes_test(lambda u: u.has_perm('course.teacher_view'))
def edit_course(request, course_slug):

    EditCourseFormSet = modelformset_factory(Course, max_num=1, extra=0,)
    if request.method == 'POST':
        formset = EditCourseFormSet(request.POST, request.FILES, 
                                    queryset=Course.objects.filter(slug=course_slug))
        if formset.is_valid():
            formset.save()
    else:
        formset = EditCourseFormSet(queryset=Course.objects.filter(slug=course_slug))

    return render_to_response('teacher/edit_course.html',
        {'formset': formset},
        context_instance=RequestContext(request))


@login_required
@user_passes_test(lambda u: u.has_perm('course.teacher_view'))
def edit_course_complete(request, course_slug):
    course = Course.objects.get(slug=course_slug)
    return render_to_response('teacher/edit_course_complete.html',
        {'slug': course_slug},
        context_instance=RequestContext(request))



@login_required
@user_passes_test(lambda u: u.has_perm('course.teacher_view'))
def teacher_enroll(request):
    """Enroll Student in class"""
    pass


@login_required
@user_passes_test(lambda u: u.has_perm('course.teacher_view'))    
def add_course(request):
    pass


