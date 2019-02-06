import course_api


def get_scotty_data(semester):
    assert(semester in ["F", "S", "M1", "M2"])
    global scotty_data
    scotty_data = course_api.get_course_data(semester)
    return scotty_data


def create_course_documents(scotty_data):
    # TODO: isolate course and events
    pass


def create_event_documents(scotty_data):
    pass


def main():
    # TODO: fix this later
    semester = "S"
