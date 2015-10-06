# jobber
Python utility for scheduling many jobs to run in sequence.

Dependences:
- redis
- yaml

The framework has five parts.
- A redis server through which everything communicates.
- A library which is used by jobs to communicate with the launcher.
- A yaml file which specifies which jobs to run, and what resources are available.
- A `launch.py` script that points to that yaml file.
- A `progress.py` which tells you how many jobs are left.

## Workflow
### Summary
- Add `jobber.JobClient` to your jobs.
- Make a `launch.yml` file, to list your jobs and desired command.
- Launch the redis server.
- Launch the jobs with `launch.py`.
- Check progress of the jobs with `progress.py`.

### Details
Have your jobs talk to the library by giving them the form:
```python
#/path/to/job1.py
from redis import Redis
from jobber import jobber

client = Redis()
job_client = jobber.JobClient(client=client)

# Do stuff

job_client.done()
```

Then create a `launch.yml` file of the form:
```yml
command: 'THEANO_FLAGS="floatX=float32,device={resource},nvcc.fastmath=True" python -u {job} &'
root: '.'
jobs:
  - /path/to/job1.py
  - /path/to/job2.py
  - /path/to/job3.py
resources:
  - gpu0
  - gpu1
```

Next launch the redis server using:
```shell
redis-server
```

Then run the jobber launch script in the directory where the jobs are:
```shell
cd /
python /code/jobber/jobber/scripts/launch.py --path /path/to/launch.yml
```

Things should start running. To check on their progress you can run:
```shell
python /code/jobber/jobber/scripts/progress.py
```