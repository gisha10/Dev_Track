import json
import os

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from issues.models import Reporter, Issue, CriticalIssue, LowPriorityIssue


ISSUES_FILE = os.path.join(settings.BASE_DIR, 'issues.json')
REPORTERS_FILE = os.path.join(settings.BASE_DIR, 'reporters.json')


def read_file(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def write_file(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)


def get_next_id(records):
    if not records:
        return 1
    return max(r['id'] for r in records) + 1


@csrf_exempt
def reporters(request):
    if request.method == 'GET':
        return get_reporters(request)
    elif request.method == 'POST':
        return create_reporter(request)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def get_reporters(request):
    all_reporters = read_file(REPORTERS_FILE)
    reporter_id = request.GET.get('id')

    if reporter_id is None:
        return JsonResponse(all_reporters, safe=False, status=200)

    try:
        reporter_id = int(reporter_id)
    except ValueError:
        return JsonResponse({'error': 'id must be a number'}, status=400)

    for reporter in all_reporters:
        if reporter['id'] == reporter_id:
            return JsonResponse(reporter, status=200)

    return JsonResponse({'error': 'Reporter not found'}, status=404)


def create_reporter(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    all_reporters = read_file(REPORTERS_FILE)
    new_id = data.get('id', get_next_id(all_reporters))

    for r in all_reporters:
        if r['id'] == new_id:
            return JsonResponse({'error': 'Reporter with this id already exists'}, status=400)

    reporter = Reporter(
        id=new_id,
        name=data.get('name', ''),
        email=data.get('email', ''),
        team=data.get('team', ''),
    )

    try:
        reporter.validate()
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

    all_reporters.append(reporter.to_dict())
    write_file(REPORTERS_FILE, all_reporters)

    return JsonResponse(reporter.to_dict(), status=201)


@csrf_exempt
def issues(request):
    if request.method == 'GET':
        return get_issues(request)
    elif request.method == 'POST':
        return create_issue(request)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def get_issues(request):
    all_issues = read_file(ISSUES_FILE)
    issue_id = request.GET.get('id')
    status = request.GET.get('status')

    if issue_id is not None:
        try:
            issue_id = int(issue_id)
        except ValueError:
            return JsonResponse({'error': 'id must be a number'}, status=400)

        for issue in all_issues:
            if issue['id'] == issue_id:
                return JsonResponse(issue, status=200)
        return JsonResponse({'error': 'Issue not found'}, status=404)

    if status is not None:
        filtered = [i for i in all_issues if i['status'] == status]
        return JsonResponse(filtered, safe=False, status=200)

    return JsonResponse(all_issues, safe=False, status=200)


def create_issue(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    all_issues = read_file(ISSUES_FILE)
    new_id = data.get('id', get_next_id(all_issues))

    for i in all_issues:
        if i['id'] == new_id:
            return JsonResponse({'error': 'Issue with this id already exists'}, status=400)

    # reporter has to exist before they can file an issue
    reporter_id = data.get('reporter_id')
    all_reporters = read_file(REPORTERS_FILE)
    if not any(r['id'] == reporter_id for r in all_reporters):
        return JsonResponse({'error': 'Reporter not found'}, status=404)

    args = dict(
        id=new_id,
        title=data.get('title', ''),
        description=data.get('description', ''),
        status=data.get('status', 'open'),
        priority=data.get('priority', ''),
        reporter_id=reporter_id,
    )

    if data.get('priority') == 'critical':
        issue = CriticalIssue(**args)
    elif data.get('priority') == 'low':
        issue = LowPriorityIssue(**args)
    else:
        issue = Issue(**args)

    try:
        issue.validate()
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

    all_issues.append(issue.to_dict())
    write_file(ISSUES_FILE, all_issues)

    response_data = issue.to_dict()
    response_data['message'] = issue.describe()
    return JsonResponse(response_data, status=201)
