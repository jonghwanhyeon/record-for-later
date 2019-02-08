import asyncio
import logging
import logging.handlers
import os

from datetime import datetime
from dateutil.tz import gettz
from pathlib import Path
from glob import glob

from .stream import Stream, StreamRecorder
from .schedule import Schedule


def _get_logger(name, timezone, output_path):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt='[%(asctime)s] %(levelname)s - ({name}) %(message)s'.format(name=name),
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    formatter.converter = lambda *_: datetime.now(timezone).timetuple()

    handlers = [
        logging.handlers.TimedRotatingFileHandler(
            filename=output_path / 'rfl.log',
            when='D',
            interval=1,
            backupCount=7,
        ),
        logging.StreamHandler(),
    ]

    for handler in handlers:
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def _rotate_videos(output_path, count):
    videos = sorted(glob(str(output_path / '*.mp4')), key=os.path.getctime)
    count -= 1

    if len(videos) > count:
        videos_to_remove = videos[:len(videos) - count]
        for filename in videos_to_remove:
            os.remove(filename)


async def _create_task(name, options):
    path = Path(options['output_path']) / name
    os.makedirs(path, exist_ok=True)

    timezone = gettz(options['timezone'])
    stream = Stream(name, options['url'], options['quality'])
    schedule = Schedule(options['interval'],  timezone)
    recorder = StreamRecorder(stream)

    logger = _get_logger(name, timezone, path)

    @recorder.on('start')
    def on_start():
        logger.info('Start recording')

    keep_quiet = 0
    @recorder.on('progress')
    def on_progress(progress):
        nonlocal keep_quiet

        if not keep_quiet:
            logger.info('Recording(time={time}, bitrate={bitrate})'.format(
                time=progress.time,
                bitrate=progress.bitrate,
            ))
        keep_quiet = (keep_quiet + 1) % 30

    @recorder.on('completed')
    def on_completed():
        logger.info('Recording completed!')

    while True:
        try:
            if await stream.is_live():
                _rotate_videos(path, options['rotate_count'])
                await recorder.record(path / '{:%Y-%m-%d-%H-%M-%S}.mp4'.format(datetime.now(timezone)))
        except Exception as exception:
            logger.error(exception)

        interval = schedule.interval
        logger.info('Sleeping {}s...'.format(interval) if interval else 'Waiting...')
        await schedule.next()


def app(streams):
    return asyncio.wait([
        _create_task(name, stream) for name, stream in streams.items()
    ])