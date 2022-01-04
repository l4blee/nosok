from discord.ext import commands


class CustomException(commands.CommandError):
    """
    Base class for all the exceptions below
    """
    pass


class AlreadyConnected(CustomException):
    """
    Occurs when the bot is already connected to the channel.
    """
    pass


class UserNotConnected(CustomException):
    """
    Occurs when a user isn't connected to a voice channel.
    """
    pass


class AlreadyPlaying(CustomException):
    """
    Occurs when the audio is already playing.
    """
    pass


class NoMoreTracks(CustomException):
    """
    Occurs when there are no more tracks in the queue.
    """
    pass


class NoTracksBefore(CustomException):
    """
    Occurs when there are no previous tracks.
    """
    pass


class QueueEmpty(CustomException):
    """
    Occurs when the queue is empty.
    """
    pass


class AlreadyPaused(CustomException):
    """
    Occurs when the player is already paused, but the user is trying to pause it one more time.
    """
    pass


class BotNotConnected(CustomException):
    """
    Occurs when the bot isn't connected to a voice channel yet.
    """
    pass


class TimeoutExceeded(CustomException):
    """
    Occurs, when a user chooses one of the songs more than 1 minute.
    """
    pass


class NoTracksSpecified(CustomException):
    """
    Occurs, when a user didn't specify any suggested tracks.
    """
    pass
