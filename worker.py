import course_api

COURSE_DOC_KEYS = (
    "courseid", "rundate", "department", "coreqs", "coreqs_obj",
    "prereqs", "prereqs_obj", "semester", "year", "units", "desc", "name", "notes"
)


def get_scotty_data(semester):
    assert (semester in ["F", "S", "M1", "M2"])
    # global scotty_data
    scotty_data = course_api.get_course_data(semester)
    return scotty_data


def create_course_documents(scotty_data):
    documents = []
    courses = scotty_data['courses']
    rundate = scotty_data['rundate']
    for courseid, course in courses.items():
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


def create_event_documents(data):
    pass


def main():
    # TODO: fix this later
    semester = "M1"
    scotty_data = get_scotty_data(semester)
    print(create_course_documents(scotty_data))
