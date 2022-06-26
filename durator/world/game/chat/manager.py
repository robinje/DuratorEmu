""" Simple chat manager.

Does not handle localisation or anything. There will be basic channel support,
maybe, but in the meantime the common channel is global to the server.
"""

import threading

from durator.common.log import LOG
from durator.world.game.chat.channel import Channel
from durator.world.game.chat.message import ChatMessageType, ServerChatMessage
from durator.world.game.chat.notification import Notification, NotificationType
from durator.world.world_connection_state import WorldConnectionState

INTERNAL_NAME_PREFIX_MAP = {"General - ": 1, "Trade - ": 2, "LocalDefense - ": 3}


def channels_lock(func):
    def channels_lock_decorator(self, *args, **kwargs):
        with self.channels_lock:
            return func(self, *args, **kwargs)

    return channels_lock_decorator


class ChatManager:
    def __init__(self, server):
        self.server = server
        self.channels = {}
        self.channels_lock = threading.Lock()

    # ------------------------------
    # Add new channels
    # ------------------------------

    @channels_lock
    def _add_channel(self, channel):
        self.channels[channel.name] = channel

    def create_channel(self, name, password=""):
        """Try to create a channel.

        Return:
        - 0 on success
        - 1 if a channel with that name already exists
        """
        if name not in self.get_channels_names():
            internal_id = ChatManager._get_internal_channel_id(name)
            channel = Channel(name, password, internal_id)
            self._add_channel(channel)
            return 0
        else:
            return 1

    @staticmethod
    def _get_internal_channel_id(name):
        for prefix in INTERNAL_NAME_PREFIX_MAP:
            if name.startswith(prefix):
                return INTERNAL_NAME_PREFIX_MAP[prefix]
        return 0

    # ------------------------------
    # Get channels
    # ------------------------------

    @channels_lock
    def get_channel(self, name):
        return self.channels.get(name)

    @channels_lock
    def get_channels_names(self):
        return list(self.channels.keys())

    # ------------------------------
    # Join, leave, modify channels
    # ------------------------------

    def join_channel(self, player, chan_name, password):
        """Try to add player to this channel with this password.

        Return:
        - 0 on success
        - 1 if the password is wrong
        """
        if chan_name not in self.get_channels_names():
            self.create_channel(chan_name, password)

        # This call assumes that after create_channel, the chan always exists.
        channel = self.get_channel(chan_name)
        if password == channel.password:
            with player.lock:
                player_guid = player.guid
                player_name = player.name
            LOG.info("{} joins channel '{}'.".format(player_name, channel.name))
            channel.add_member(player_guid)
            self._notify_join(channel, player_guid)
            return 0
        else:
            self.clean(chan_name)
            return 1

    def _notify_join(self, channel, joiner_guid):
        """Send to all members of this channel that a player joined."""
        members = channel.get_members()
        notification = Notification(NotificationType.JOINED, channel)
        notification.join_leave_guid = joiner_guid
        notify_packet = notification.to_packet()

        members.remove(joiner_guid)
        self.server.broadcast(notify_packet, state=WorldConnectionState.IN_WORLD, guids=members)

    def leave_channel(self, player, chan_name):
        """Try to leave channel.

        Return:
        - 0 on success
        - 1 if player wasn't on that channel to begin with
        - 2 if the channel doesn't even exist
        """
        if chan_name not in self.get_channels_names():
            return 2
        channel = self.get_channel(chan_name)

        with player.lock:
            player_guid = player.guid
            player_name = player.name

        if player_guid not in channel.get_members():
            return 1

        LOG.info(f"{player_name} leaves channel '{channel.name}'.")
        channel.remove_member(player_guid)
        self._notify_leave(channel, player_guid)
        return 0

    def _notify_leave(self, channel, leaver_guid):
        """Send to all members of this channel that a player left."""
        members = channel.get_members()
        notification = Notification(NotificationType.LEFT, channel)
        notification.join_leave_guid = leaver_guid
        notify_packet = notification.to_packet()

        self.server.broadcast(notify_packet, state=WorldConnectionState.IN_WORLD, guids=members)

    def receive_message(self, sender, message):
        """Register a received chat message for that sender (GUID).

        Return:
        - 0 on success
        - 1 if not on the channel
        - 2 if channel name is invalid
        - 3 on unhandled message type
        - 4 if muted (not implemented)
        """
        if message.message_type is ChatMessageType.CHANNEL:
            channel = self.get_channel(message.channel_name)
            if channel is not None:
                return self._send_channel_message(channel, sender, message)
            else:
                return 2
        elif (
            message.message_type is ChatMessageType.SAY
            or message.message_type is ChatMessageType.YELL
            or message.message_type is ChatMessageType.EMOTE
        ):
            return self._send_global_chat_message(sender, message)
        else:
            return 3

    def _send_channel_message(self, channel, sender, message):
        members = channel.get_members()
        if sender not in members:
            return 1

        server_message = ServerChatMessage()
        server_message.load_client_message(message)
        server_message.sender_guid = sender
        message_packet = server_message.to_packet()

        self.server.broadcast(message_packet, state=WorldConnectionState.IN_WORLD, guids=members)
        return 0

    def _send_global_chat_message(self, sender, message):
        server_message = ServerChatMessage()
        server_message.load_client_message(message)
        server_message.sender_guid = sender
        message_packet = server_message.to_packet()

        self.server.broadcast(message_packet, state=WorldConnectionState.IN_WORLD)
        return 0

    # ------------------------------
    # Remove channels
    # ------------------------------

    @channels_lock
    def _remove_channel(self, name):
        del self.channels[name]

    def clean(self, chan_name=None):
        """Remove all empty channels, or chan_name if provided."""
        if chan_name is not None:
            self._remove_channel_if_empty(chan_name)
        else:
            channels_names = self.get_channels_names()
            for chan_name in channels_names:
                self._remove_channel_if_empty(chan_name)

    def _remove_channel_if_empty(self, name):
        channel = self.get_channel(name)
        if channel is None:
            return
        if not channel.get_members():
            self._remove_channel(name)
