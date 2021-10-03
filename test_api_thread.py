
from communicate.issue_thread import IssueThread
import communicate.issueType as issueType
import time
issue_thread = IssueThread(1)
issue_thread.start()
while True:
    frame = 1
    issue_thread.set_set_issue(frame,issueType.OBSTACLE_DETECTED)
    time.sleep(3)
    issue_thread.reset_status()
    time.sleep(1)
    issue_thread.set_set_issue(frame,issueType.NO_LANE_DETECT)
    time.sleep(3)
    break

issue_thread.stop()