import argparse
import os

from redis import Redis
import yaml

from jobber import jobber

parser = argparse.ArgumentParser(prog='Jobber',
                                 description='Utily to launch jobs.')

parser.add_argument('--path',
                    type=str,
                    help='Path for yml file.')

args = parser.parse_args()

if __name__ == '__main__':

    client = Redis()

    path = args.path

    with open(path, 'r') as f:
        config = yaml.load(f)

    launcher = jobber.JobLauncher(client=client,
                                  cmd=config['command'])

    jobs = [os.path.join(config['root'], job)
            for job in config['jobs']]

    launcher.add(jobs)
    launcher.add_resources(config['resources'])

    launcher.run()

    launcher.done()