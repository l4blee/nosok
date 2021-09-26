from discord.ext import commands


class AlreadyConnectedToChannel(commands.CommandError):
    """
    Player is already connected to the channel.
    """
    pass

class NotConnectedToChannel(commands.CommandError):
    """
    Occurs when a user isn't connected to a voice channel.
    """
    pass

class AlreadyPlayinAudio(commands.CommandError):
    """
    Occurs when the audio is already playing.
    """
    pass

class NoMoreTracks(commands.CommandError):
    """
    Occurs when there're no more tracks in the queue.
    """
    pass

class NoPreviousTracks(commands.CommandError):
    """
    Occurs when there're no previous tracks.
    """
    pass

class QueueEmpty(commands.CommandError):
    """
    Occurs when the queue is empty.
    """
    pass

class PlayerIsAlreadyPaused(commands.CommandError):
    """
    Occurs when the player is already paused, but the user is trying to pause it one more time.
    """
    pass

class BotNotConnectedToChannel(commands.CommandError):
    """
    Occurs when the bot isn't connected to a voice channel yet.
    """
    pass

class TimeoutExceeded(commands.CommandError):
    """
    Occurs, when a user chooses one of the songs more than 1 minute.
    """
    pass
