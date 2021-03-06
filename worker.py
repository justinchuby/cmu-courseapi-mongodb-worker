import datetime
import copy
from pymongo import MongoClient
from pymongo import DeleteMany, UpdateOne
import course_api
import config

DEBUG = config.DEBUG

if config.SENTRY_DSN:
    import sentry_sdk
    sentry_sdk.init(config.SENTRY_DSN)
    print("[Worker] Sentry imported")

COURSE_DOC_KEYS = (
    "courseId", "rundate", "department", "coreqs", "coreqsObj",
    "prereqs", "prereqsObj", "semester", "year", "units", "desc", "name", "notes"
)

SEMESTERS = ("F", "S", "M1", "M2")


def get_scotty_courses(semester):
    assert (semester in SEMESTERS)
    scotty_data = course_api.get_course_data(semester)
    return scotty_data


def create_course_documents(scotty_data, rundate):
    documents = []
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


def create_meeting_documents(scotty_data, rundate):
    documents = []

    for courseid, course in scotty_data.items():
        def convert_meeting(meeting):
            meeting = copy.deepcopy(meeting)
            meeting['courseId'] = courseid
            meeting['rundate'] = rundate
            meeting['year'] = course['year']
            meeting['semester'] = course['semester']
            for t in meeting['times']:
                t['begin'] = convert_time(t['begin'])
                t['end'] = convert_time(t['end'])
            return meeting

        meetings = list(map(convert_meeting, course['meetings']))
        documents += meetings
    return documents


def convert_time(time_string: str) -> int:
    # Check for none
    if time_string:
        t = datetime.datetime.strptime(time_string, "%I:%M%p")
        return t.hour * 60 + t.minute


def upload_courses(db, documents):
    write_ops = []
    for doc in documents:
        write_ops.append(UpdateOne(
            {
                'courseId': doc['courseId'],
                'semester': doc['semester'],
                'year': doc['year']
            },
            {'$set': doc}, upsert=True
        ))
    result = db["courses"].bulk_write(write_ops)
    print('[Worker] Updated', result.modified_count, 'in courses')


def upload_meetings(db, documents):
    deleted_set = set()
    write_ops = []
    # Delete the old meetings first
    for doc in documents:
        course_marker = (doc['semester'], doc['year'], doc['courseId'])
        if course_marker not in deleted_set:
            write_ops.append(DeleteMany(
                {
                    'courseId': doc['courseId'],
                    'semester': doc['semester'],
                    'year': doc['year'],
                }
            ))
            deleted_set.add(course_marker)

    # Then add the new documents
    result = db['meetings'].bulk_write(write_ops)
    print('[Worker] Deleted', result.deleted_count, 'in meetings')
    result = db['meetings'].insert_many(documents)
    print('[Worker] Added', len(result.inserted_ids), 'in meetings')


def main():
    rundate = datetime.datetime.today()

    # Connect to database
    client = MongoClient(config.MONGO_URI)
    db = client[config.DB_NAME]

    # Get data from each semesters first
    course_documents = []
    meeting_documents = []

    for semester in SEMESTERS:
        if DEBUG:
            global scotty_data
        scotty_data = get_scotty_courses(semester)

        # TODO: Validate data
        course_documents += create_course_documents(scotty_data, rundate)
        meeting_documents += create_meeting_documents(scotty_data, rundate)

    upload_courses(db, course_documents)
    upload_meetings(db, meeting_documents)
