import course_api

def generate_from_course_api(semester):
    assert(semester in ["F", "S", "M1", "M2"])
    global scotty_data
    scotty_data = cmu_course_api.get_course_data(semester)

def main():
    pass