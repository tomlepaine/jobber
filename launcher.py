import subprocess
import argparse
import time

from redis import Redis
import yaml

parser = argparse.ArgumentParser(prog='Jobber',
                                 description='Utily to launch jobs.')

parser.add_argument('--path',
                    type=str,
                    help='Path for yml file.')

args = parser.parse_args()


class JobLauncher(object):
    def __init__(self, client, cmd):
        self.client = client
        self.client.flushall()
        self.cmd = cmd

    def add(self, names):
        self.client.lpush('todo', *names)

    def add_resources(self, names):
        self.client.lpush('available', *names)
        print 'Added %d resources.' % self.client.llen('available')

    def run(self):
        num_jobs = self.client.llen('todo')

        print 'Running %d jobs.' % num_jobs
        while self.client.llen('done') != num_jobs:
            if self.client.llen('available'):  # If resource available.
                job = self.client.lpop('todo')  # pop a job off the todo queue.
                resource = self.client.lpop('available')
                if job:
                    self._run_job(job, resource)

    def done(self):
        num_done = self.client.llen('done')
        print 'Finished %d jobs.' % num_done

    def _run_job(self, job, resource):
        self.client.set(job, resource)
        cmd = self.cmd.format(job=job,
                              resource=resource)
        failed = subprocess.call(cmd, shell=True)
        assert(not failed)
        print cmd
        self.client.lpush('running', job)


class JobClient(object):
    def __init__(self, client, job):
        self.client = client
        self.job = job
        self.resource = client.get(job)
        self.tic = time.time()

    def done(self):
        self.client.lpush('available', self.resource)
        self.client.lrem('running', self.job)
        self.client.lpush('done', self.job)

        toc = time.time()
        self.client.set('Time:%s' % self.job, toc - self.tic)


class JobProgress(object):
    def __init__(self, client):
        self.client = client

    def running(self):
        return self.client.lrange('running', 0, -1)

    def todo(self):
        return self.client.lrange('todo', 0, -1)

    def done(self):
        return self.client.lrange('done', 0, -1)

    def times(self):
        done = self.done()

        return {job: self.client.get('Time:%s' % job) for job in done}

    def _print(self, items):
        for item in items:
            print item

    def _print_dict(self, my_dict):
        for key, value in my_dict.iteritems():
            print '{key} : {value}'.format(key=key,
                                           value=value)

    def run(self):
        print '-- Running --'
        self._print(self.running())
        print '-- Todo --'
        self._print(self.todo())
        print '-- Done --'
        self._print_dict(self.times())

if __name__ == '__main__':

    client = Redis()

    path = args.path

    with open(path, 'r') as f:
        config = yaml.load(f)

    launcher = JobLauncher(client=client,
                           cmd=config['command'])

    launcher.add(config['jobs'])
    launcher.add_resources(config['resources'])

    launcher.run()

    launcher.done()