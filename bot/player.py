import logging
import warnings

from io import BytesIO
from audioop import mul

from discord.player import PCMVolumeTransformer, FFmpegPCMAudio, AudioSource
from pydub import AudioSegment
from numpy import std, mean, errstate

logger = logging.getLogger('player')


class BassVolumeTransformer(AudioSource):
    def __init__(self, original, volume: float = 1.0, bass_accentuate: float = 0):
        if not isinstance(original, AudioSource):
            raise TypeError(f'expected AudioSource not {original.__class__.__name__}.')

        if original.is_opus():
            raise ClientException('AudioSource must not be Opus encoded.')

        self.original = original
        self._volume = volume
        self._bass = bass_accentuate
        
        # 100Hz as basic bass freq to avoid issues, when bass_factor is 0.
        self._last_bass_factor = 100

    @property
    def volume(self) -> float:
        """Retrieves or sets the volume as a floating point percentage (e.g. ``1.0`` for 100%)."""
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = max(min(value, 2.0),
                           0.0)

    @property
    def bass_accentuate(self) -> float:
        return self._bass
    
    @bass_accentuate.setter
    def bass_accentuate(self, value: float):
        self._bass = min(max(value, -20), 200)

    def _bass_boost(self, sample: bytes) -> bytes:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            if self._bass == 0:
                return sample

            sample = AudioSegment.from_raw(
                BytesIO(sample),
                sample_width=2,
                frame_rate=48000,
                channels=2
            )

            sample_list = sample.get_array_of_samples()

            est_mean = mean(sample_list)
            est_std = 3 * std(sample_list) / (2 ** 0.5)
            bass_factor = int(est_std - est_mean * 0.015) or self._last_bass_factor
            self._last_freq = bass_factor

            lower = sample.low_pass_filter(bass_factor)
            gain = self._bass - sample.dBFS
            lower = lower.apply_gain(gain)

            output = sample.overlay(lower)

            return output.raw_data

    def read(self):
        orig = self.original.read()  # Getting original sound
        ret = mul(orig, 2, self.volume)  # Volume adjusting
        return self._bass_boost(ret)  # Returning with bass boost

    def cleanup(self):
        self.original.cleanup()
