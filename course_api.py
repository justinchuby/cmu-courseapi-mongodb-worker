from datetime import date
from parse_descs import get_course_desc
from parse_schedules import parse_schedules

# imports used for multithreading
import threading
from queue import Queue
from os import cpu_count
from queue import Empty


# Constants
SEMESTER_ABBREV = {
    'Spring': 'S',
    'Fall': 'F',
    'Summer': 'M'
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
    year = schedules['semester'].split(' ')[-1][2:]

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

            print('Getting description for ' + _course['num'])

            desc = get_course_desc(_course['num'], semester, year)
            retry_count = RETRY
            if desc is None and retry_count > 0:
                # Retry getting desc
                print('    Retrying ' + _course['num'])
                retry_count -= 1
                desc = get_course_desc(_course['num'], semester, year)

            desc['name'] = _course['title']

            try:
                desc['units'] = float(_course['units'])
            except ValueError:
                desc['units'] = None

            desc['department'] = _course['department']
            desc['lectures'] = _course['lectures']
            desc['sections'] = _course['sections']
            names_dict = desc.pop('names_dict', {})

            # Replace names of instructors with their full names
            for key in ('lectures', 'sections'):
                for meeting in desc[key]:
                    if meeting['name'] in names_dict:
                        meeting['instructors'] = names_dict[meeting['name']]

            number = _course['num'][:2] + '-' + _course['num'][2:]
            with lock:
                courses[number] = desc
            queue.task_done()

    for course in schedules['schedules']:
        queue.put(course)

    print("running on " + str(count) + " threads")
    for _ in range(count):
        thread = threading.Thread(target=run)
        thread.setDaemon(True)
        thread.start()

    queue.join()

    return {'courses': courses, 'rundate': str(date.today()),
            'semester': schedules['semester']}


# @function get_course_data
# @brief Used for retrieving all information from the course-api for a given
#        semester.
# @param semester: The semester to get data for. Must be one of [S, M1, M2, F].
# @return Object containing all course-api data - see README.md for more
#        information.
def get_course_data(semester):
    schedules = parse_schedules(semester)
    return aggregate(schedules)
