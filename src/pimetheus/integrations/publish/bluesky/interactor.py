from typing import cast

import structlog
from atproto.exceptions import AtProtocolError
from atproto_client.models.app.bsky.feed.like import CreateRecordResponse as LikeResponse
from atproto_client.models.app.bsky.feed.repost import CreateRecordResponse as RepostResponse
from atproto_client.models.app.bsky.graph.follow import CreateRecordResponse as FollowResponse

from pimetheus.integrations.publish.bluesky.client import BlueskyAPIClient

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


class BlueskyInteractor:
    """
    Interact with Bluesky users and posts.

    Attributes:
        blueskyapi (BlueskyAPIClient): API client.
        client (Client): Underlying client.
    """

    def __init__(self, blueskyapi: BlueskyAPIClient) -> None:
        self.blueskyapi = blueskyapi
        self.client = blueskyapi.client

    def follow(self, did: str) -> FollowResponse | bool:
        """
        Follow user by DID.

        Parameters:
            did (str): User DID.

        Returns:
            FollowResponse | bool: API response or offline flag.

        Raises:
            AtProtocolError: If request fails.
        """

        if self.blueskyapi.settings.pimetheus.offline:
            logger.info("Followed TEST", did=did)
            return self.blueskyapi.settings.pimetheus.offline
        try:
            response = self.blueskyapi.execute_with_retry(lambda: self.client.follow(did), action="following")
            logger.info("Followed user", did=did, response=response)
            return response
        except AtProtocolError:
            logger.error("Failed to follow actor", did=did)
            raise

    def like(self, uri: str, cid: str) -> LikeResponse | bool:
        """
        Like post.

        Parameters:
            uri (str): Post URI.
            cid (str): Content ID.

        Returns:
            LikeResponse | bool: API response or offline flag.

        Raises:
            AtProtocolError: If request fails.
        """

        if self.blueskyapi.settings.pimetheus.offline:
            logger.info("Liked TEST", uri=uri, cid=cid)
            return self.blueskyapi.settings.pimetheus.offline
        try:
            response = self.blueskyapi.execute_with_retry(lambda: self.client.like(uri, cid), action="like")
            logger.info("Liked post", uri=uri, cid=cid, response=response)
            return response
        except AtProtocolError:
            logger.error("Failed to like post", uri=uri, cid=cid)
            raise

    def repost(self, uri: str, cid: str) -> RepostResponse | bool:
        """
        Repost content.

        Parameters:
            uri (str): Post URI.
            cid (str): Content ID.

        Returns:
            RepostResponse | bool: API response or offline flag.

        Raises:
            AtProtocolError: If request fails.
        """

        if self.blueskyapi.settings.pimetheus.offline:
            logger.info("Reposted TEST", uri=uri, cid=cid)
            return self.blueskyapi.settings.pimetheus.offline
        try:
            response = self.blueskyapi.execute_with_retry(lambda: self.client.repost(uri, cid), action="repost")
            logger.info("Reposted", uri=uri, cid=cid, response=response)
            return response
        except AtProtocolError:
            logger.error("Failed to repost post", uri=uri, cid=cid)
            raise

    def unfollow(self, follow_uri: str) -> bool:
        """
        Unfollow user.

        Parameters:
            follow_uri (str): Follow record URI.

        Returns:
            bool: Operation result or offline flag.

        Raises:
            AtProtocolError: If request fails.
        """

        if self.blueskyapi.settings.pimetheus.offline:
            logger.info("Unfollowed TEST", follow_uri=follow_uri)
            return self.blueskyapi.settings.pimetheus.offline
        try:
            response = self.blueskyapi.execute_with_retry(lambda: self.client.unfollow(follow_uri), action="unfollow")
            logger.info("Unfollowed user", follow_uri=follow_uri, response=response)
            return cast(bool, response)
        except AtProtocolError:
            logger.error("Failed to unfollow actor", follow_uri=follow_uri)
            raise

    def unlike(self, like_uri: str) -> bool:
        """
        Unlike post.

        Parameters:
            like_uri (str): Like record URI.

        Returns:
            bool: Operation result or offline flag.

        Raises:
            AtProtocolError: If request fails.
        """

        if self.blueskyapi.settings.pimetheus.offline:
            logger.info("Unliked TEST", like_uri=like_uri)
            return self.blueskyapi.settings.pimetheus.offline
        try:
            response = self.blueskyapi.execute_with_retry(lambda: self.client.unlike(like_uri), action="unlike")
            logger.info("Unliked post", like_uri=like_uri, response=response)
            return cast(bool, response)
        except AtProtocolError:
            logger.error("Failed to unlike post", like_uri=like_uri)
            raise
