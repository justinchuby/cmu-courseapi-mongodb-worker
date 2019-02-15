# Adapted from ScottyLabs Course API. https://github.com/ScottyLabs/course-api

from parse_descs import get_course_desc
from parse_schedules import parse_schedules

# imports used for multithreading
import threading
from queue import Queue
from os import cpu_count
from queue import Empty


# Constants
SEMESTER_ABBREV = {
    'spring': 'S',
    'fall': 'F',
    'summer': 'M'
}
RETRY = 3


# @function aggregate
# @brief Combines the course descriptions and schedules into one object.
# @param schedules: Course schedules object as returned by parse_descs.
# @return An object containing the aggregate of the three datasets.
def aggregate(schedules):
    courses = {}

    semester = schedules['semester'].split(' ')[0]
    semester = SEMESTER_ABBREV[semester]
    year = str(schedules['year'])[2:]

    count = cpu_count() * 4
    lock = threading.Lock()
    queue = Queue()

    if count is None or count < 16:
        count = 16

    def run():
        while True:
            try:
                _course = queue.get(timeout=4)
            except Empty:
                return

            print('Getting description for', _course['num'], semester, year)

            course_with_desc = {}

            desc = get_course_desc(_course['num'], semester, year)
            retry_count = RETRY
            while desc is None and retry_count > 0:
                # Retry getting desc
                print('    Retrying ' + _course['num'])
                retry_count -= 1
                desc = get_course_desc(_course['num'], semester, year)

            if desc is not None:
                names_dict = desc.pop('names_dict', {})
                # Replace names of instructors with their full names
                for meeting in _course['meetings']:
                    if meeting['name'] in names_dict:
                        meeting['instructors'] = names_dict[meeting['name']]
                course_with_desc = desc

            course_with_desc['name'] = _course['title']

            try:
                course_with_desc['units'] = float(_course['units'])
            except ValueError:
                course_with_desc['units'] = None

            course_with_desc['department'] = _course['department']
            course_with_desc['meetings'] = _course['meetings']
            course_with_desc['semester'] = _course['semester']
            course_with_desc['year'] = _course['year']

            number = _course['num'][:2] + '-' + _course['num'][2:]
            with lock:
                courses[number] = course_with_desc
            queue.task_done()

    for course in schedules['schedules']:
        queue.put(course)

    print("running on " + str(count) + " threads")
    for _ in range(count):
        thread = threading.Thread(target=run)
        thread.setDaemon(True)
        thread.start()

    queue.join()

    return courses


# @function get_course_data
# @brief Used for retrieving all information from the course-api for a given
#        semester.
# @param semester: The semester to get data for. Must be one of [S, M1, M2, F].
# @return Object containing all course-api data - see README.md for more
#        information.
def get_course_data(semester):
    schedules = parse_schedules(semester)
    return aggregate(schedules)
