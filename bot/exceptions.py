from enum import Enum

from base import CustomException, ERROR_COLOR, BASE_COLOR


class ExceptionType(Enum):
    NOTIFICATION = BASE_COLOR
    ERROR = ERROR_COLOR


class AlreadyConnected(CustomException):
    """
    Occurs when the bot is already connected to the channel.
    """
    description = 'I am already connected to a voice channel.'
    type_ = ExceptionType['ERROR']


class UserNotConnected(CustomException):
    """
    Occurs when a user isn't connected to a voice channel.
    """
    description = 'Connect to a voice channel first.'
    type_ = ExceptionType['ERROR']


class AlreadyPlaying(CustomException):
    """
    Occurs when the audio is already playing.
    """
    description = 'I am already playing an audio!'
    type_ = ExceptionType['ERROR']


class QueueEnded(CustomException):
    """
    Occurs when there are no more tracks in the queue.
    """
    description = 'The queue has ended'
    type_ = ExceptionType['NOTIFICATION']


class NoTracksBefore(CustomException):
    """
    Occurs when there are no previous tracks.
    """
    description = 'There are no tracks before the current one.'
    type_ = ExceptionType['NOTIFICATION']


class QueueEmpty(CustomException):
    """
    Occurs when the queue is empty.
    """
    description = 'There are no songs in the queue.'
    type_ = ExceptionType['NOTIFICATION']


class AlreadyPaused(CustomException):
    """
    Occurs when the player is already paused, but the user is trying to pause it one more time.
    """
    description = 'The audio is already paused'
    type_ = ExceptionType['ERROR']


class BotNotConnected(CustomException):
    """
    Occurs when the bot isn't connected to a voice channel yet.
    """
    description = 'I am not connected to a voice channel yet!'
    type_ = ExceptionType['ERROR']


class NoTracksSpecified(CustomException):
    """
    Occurs, when a user didn't specify any suggested tracks.
    """
    description = 'No tracks were specified.'
    type_ = ExceptionType['NOTIFICATION']


class QueryTooShort(CustomException):
    """
    Occurs, when a user tries to search a song with too short query (<10 symbols).
    """
    description = 'Query is too short.'
    type_ = ExceptionType['ERROR']


class WrongLocale(CustomException):
    """
    """
    description = 'This language is not supported.'
    type_ = ExceptionType['ERROR']
