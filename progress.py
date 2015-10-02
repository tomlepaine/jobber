from launcher import JobProgress

from redis import Redis

client = Redis()

progress = JobProgress(client=client)
progress.run()
