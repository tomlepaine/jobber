from jobber import jobber

from redis import Redis

client = Redis()

progress = jobber.JobProgress(client=client)
progress.run()
