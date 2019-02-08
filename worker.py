import datetime
import copy
import course_api

COURSE_DOC_KEYS = (
    "courseid", "rundate", "department", "coreqs", "coreqs_obj",
    "prereqs", "prereqs_obj", "semester", "year", "units", "desc", "name", "notes"
)


def get_scotty_courses(semester):
    assert (semester in ["F", "S", "M1", "M2"])
    # global scotty_data
    scotty_data = course_api.get_course_data(semester)
    return scotty_data


def create_course_documents(scotty_data):
    documents = []
    rundate = datetime.date.today()
    for courseid, course in scotty_data.items():
        document = {}
        for key in COURSE_DOC_KEYS:
            if key == 'courseid':
                document[key] = courseid
            elif key == 'rundate':
                document[key] = rundate
            else:
                document[key] = course[key]
        documents.append(document)
    return documents


def create_meeting_documents(scotty_data):
    documents = []
    rundate = datetime.date.today()

    for courseid, course in scotty_data.items():
        def convert_meeting(meeting):
            meeting = copy.copy(meeting)
            meeting['courseid'] = courseid
            meeting['rundate'] = rundate
            meeting['year'] = course['year']
            meeting['semester'] = course['semester']
            return meeting

        meetings = list(map(convert_meeting, course['meetings']))
        documents = documents + meetings
    return documents


def main():
    # TODO: fix this later
    semester = "M2"
    scotty_data = get_scotty_courses(semester)
    print(create_meeting_documents(scotty_data))
