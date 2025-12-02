from celery import shared_task

@shared_task
def test_task(name):
    print(f"Hello {name}, Celery task executed!")
    return "Done"
