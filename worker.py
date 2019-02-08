import datetime
import copy
import course_api
from pymongo import MongoClient

COURSE_DOC_KEYS = (
    "courseId", "rundate", "department", "coreqs", "coreqsObj",
    "prereqs", "prereqsObj", "semester", "year", "units", "desc", "name", "notes"
)

SEMESTERS = ("F", "S", "M1", "M2")


def get_scotty_courses(semester):
    assert (semester in SEMESTERS)
    scotty_data = course_api.get_course_data(semester)
    return scotty_data


def create_course_documents(scotty_data):
    documents = []
    rundate = datetime.date.today()
    for courseid, course in scotty_data.items():
        document = {}
        for key in COURSE_DOC_KEYS:
            if key == 'courseId':
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
            meeting['courseId'] = courseid
            meeting['rundate'] = rundate
            meeting['year'] = course['year']
            meeting['semester'] = course['semester']
            return meeting

        meetings = list(map(convert_meeting, course['meetings']))
        documents += meetings
    return documents


def main():
    # Connect to database
    client = MongoClient('mongodb://localhost:27017/')
    # TODO: configure database name
    db = client['courseapi']

    # Get data from each semesters first
    course_documents = []
    meeting_documents = []
    for semester in SEMESTERS:
        scotty_data = get_scotty_courses(semester)

        # TODO: Validate data

        course_documents += create_course_documents(scotty_data)
        meeting_documents += create_meeting_documents(scotty_data)

    for doc in course_documents:
        # Upload to MongoDB
        result = db.courses.update_one(
            {
                'courseId': doc['courseId'],
                'semester': doc['semester'],
                'yera': doc['year']
            },
            {'$set': doc}, upsert=True
        )
    for doc in meeting_documents:
        # TODO: log results
        result = db.meetings.update_one(
            {
                'courseId': doc['courseId'],
                'semester': doc['semester'],
                'yera': doc['year']
            },
            {'$set': doc}, upsert=True
        )
