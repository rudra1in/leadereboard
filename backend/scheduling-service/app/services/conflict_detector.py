from sqlalchemy.orm import Session

from app.models.schedule import Schedule


def check_conflict(
    db: Session,
    court_id,
    referee_id,
    start_time,
    end_time,
    schedule_id=None
):
    query = db.query(Schedule).filter(
        Schedule.start_time < end_time,
        Schedule.end_time > start_time
    )

    if schedule_id:
        query = query.filter(
            Schedule.id != schedule_id
        )

    schedules = query.all()

    for schedule in schedules:

        if schedule.court_id == court_id:
            return True, "Court is already allocated"

        if schedule.referee_id == referee_id:
            return True, "Referee is already assigned"

    return False, None