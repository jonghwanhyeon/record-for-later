import asyncio
import itertools
import os

from functools import partial
from ffmpeg import FFmpeg
from pyee import EventEmitter

def _streamlink(url, quality=None, **kwargs):
    kwargs = {'--{}'.format(key): value for key, value in kwargs.items()}

    parameters = list(itertools.chain.from_iterable(
        (key, str(value)) if not isinstance(value, bool) else (key, )
        for key, value in kwargs.items()
    ))

    parameters.append(url)
    if quality:
        parameters.append(quality)

    return asyncio.create_subprocess_exec(
        'streamlink',
        *parameters,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
    )


class Stream:
    def __init__(self, name, url, quality='best'):
        self.name = name
        self.url = url
        self.quality = quality

    async def is_live(self):
        streamlink_process = await _streamlink(self.url, json=True)
        await streamlink_process.wait()
        return streamlink_process.returncode == 0


class StreamRecorder(EventEmitter):
    def __init__(self, stream):
        super().__init__()
        self.stream = stream

    async def record(self, filename):
        streamlink_process = await _streamlink(self.stream.url, self.stream.quality, stdout=True)

        # To fix inaccurate timestamps, record videos via ffmpeg
        ffmpeg = FFmpeg().input('pipe:0').output(os.fspath(filename), c='copy')
        self._set_handlers(ffmpeg)

        await ffmpeg.execute(streamlink_process.stdout)

    def _set_handlers(self, ffmpeg):
        ffmpeg.on('start', lambda _: self.emit('start'))
        for event in ('stderr', 'progress', 'completed', 'terminated'):
            ffmpeg.on(event, partial(self.emit, event))