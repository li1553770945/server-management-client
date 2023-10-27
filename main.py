from apscheduler.schedulers.blocking import BlockingScheduler
from job import job
import yaml
from datetime import datetime
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-mode', default='debug')
args = parser.parse_args()
mode = args.mode

if __name__ == '__main__':

    print(f"start with mode:{mode}")
    with open('config.yaml', 'r') as f:
        config = yaml.load(f.read(),Loader=yaml.FullLoader)
        config = config[mode]
        scheduler = BlockingScheduler()
        scheduler.add_job(job, 'interval', id='sync', seconds=config['client']['interval_seconds'],args=[config],next_run_time=datetime.now())
        scheduler.start()
