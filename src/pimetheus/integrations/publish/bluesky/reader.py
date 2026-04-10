from typing import Any, cast

import structlog
from atproto.exceptions import AtProtocolError
from atproto_client.models.app.bsky.actor.defs import ProfileView, ProfileViewDetailed
from atproto_client.models.app.bsky.feed.defs import FeedViewPost, PostView
from atproto_client.models.app.bsky.feed.get_likes import Like

from pimetheus.integrations.publish.bluesky.client import BlueskyAPIClient

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


class BlueskyReader:
    """
    Read data from Bluesky.

    Attributes:
        blueskyapi (BlueskyAPIClient): API client.
        client (Client): Underlying client.
        FEED_LIMIT (int): Default query limit.
    """

    FEED_LIMIT = 10

    def __init__(self, blueskyapi: BlueskyAPIClient) -> None:
        self.blueskyapi = blueskyapi
        self.client = blueskyapi.client

    def get_profile(self, actor: str) -> ProfileViewDetailed:
        """
        Retrieve profile details.

        Parameters:
            actor (str): User handle or DID.

        Returns:
            ProfileViewDetailed: Profile data.

        Raises:
            AtProtocolError: If request fails.
        """

        try:
            profile = self.blueskyapi.execute_with_retry(
                lambda: self.client.get_profile(actor=actor), action="retrieving profile"
            )
            logger.info("Retrieved profile", actor=actor, profile=profile.display_name)
            return profile
        except AtProtocolError:
            logger.error("Failed to retrieve profile", actor=actor)
            raise

    def get_author_feed(self, actor: str) -> list[FeedViewPost]:
        """
        Retrieve author feed.

        Parameters:
            actor (str): User handle or DID.

        Returns:
            list[FeedViewPost]: Feed posts.

        Raises:
            AtProtocolError: If request fails.
        """

        try:
            response = self.blueskyapi.execute_with_retry(
                lambda: self.client.get_author_feed(actor=actor), action="retrieving author feed"
            )
            logger.info("Retrieved author feed", actor=actor)
            feed = cast(list[FeedViewPost], response.feed)
            return feed
        except AtProtocolError:
            logger.error("Failed to retrieve author feed", actor=actor)
            raise

    def get_followers(self, actor: str, limit: int | None = None) -> list[ProfileView]:
        """
        Retrieve followers.

        Parameters:
            actor (str): User handle or DID.
            limit (int | None): Max results.

        Returns:
            list[ProfileView]: Followers.

        Raises:
            AtProtocolError: If request fails.
        """

        try:
            response = self.blueskyapi.execute_with_retry(
                lambda: self.client.get_followers(actor=actor, limit=limit), action="retrieving followers"
            )
            logger.info("Retrieved author's followers", actor=actor, limit=limit)
            followers = cast(list[ProfileView], response.followers)
            return followers
        except AtProtocolError:
            logger.error("Failed to retrieve author's followers", actor=actor, limit=limit)
            raise

    def get_follows(self, actor: str, limit: int | None = None) -> list[ProfileView]:
        """
        Retrieve follows.

        Parameters:
            actor (str): User handle or DID.
            limit (int | None): Max results.

        Returns:
            list[ProfileView]: Followers.

        Raises:
            AtProtocolError: If request fails.
        """

        try:
            response = self.blueskyapi.execute_with_retry(
                lambda: self.client.get_follows(actor=actor, limit=limit), action="retrieving follows"
            )
            logger.info("Retrieved author's follows", actor=actor, limit=limit)
            follows = cast(list[ProfileView], response.follows)
            return follows
        except AtProtocolError:
            logger.error("Failed to retrieve author's follows", actor=actor, limit=limit)
            raise

    def get_likes(self, uri: str, cid: str, limit: int | None = None) -> list[Like]:
        """
        Retrieve the likes for a specific post.

        Args:
            uri (str): The post URI.
            cid (str): The content ID of the post.
            limit (int, optional): Maximum number of likes to retrieve. Defaults to all.

        Returns:
            list[Like]: List of likes for the specified post.

        Raises:
            AtProtocolError: If the request fails.
        """

        try:
            response = self.blueskyapi.execute_with_retry(
                lambda: self.client.get_likes(uri, cid, limit), action="retrieving likes"
            )
            logger.info("Retrieved likes", uri=uri, cid=cid, limit=limit)
            likes = cast(list[Like], response.likes)
            return likes
        except AtProtocolError:
            logger.error("Failed to retrieve likes", uri=uri, cid=cid, limit=limit)
            raise

    def get_reposts(self, uri: str, cid: str) -> list[ProfileView]:
        """
        Retrieve the users who reposted a specific post.

        Args:
            uri (str): The post URI.
            cid (str): The content ID of the post.

        Returns:
            list[ProfileView]: List of profiles who reposted the post.

        Raises:
            AtProtocolError: If the request fails.
        """

        try:
            response = self.blueskyapi.execute_with_retry(
                lambda: self.client.get_reposted_by(uri, cid), action="retrieving reposts"
            )
            logger.info("Retrieved reposts", uri=uri, cid=cid)
            reposts = cast(list[ProfileView], response.reposted_by)
            return reposts
        except AtProtocolError:
            logger.error("Failed to retrieve reposts", uri=uri, cid=cid)
            raise

    def get_posts(
        self,
        query: str,
        author: str | None = None,
        mentions: str | None = None,
        tag: list[str] | None = None,
        since: str | None = None,
        until: str | None = None,
    ) -> list[PostView]:
        """
        Search posts.

        Parameters:
            query (str): Search query.
            author (str | None): Author filter.
            mentions (str | None): Mentions filter.
            tag (list[str] | None): Tag filter.
            since (str | None): Start date.
            until (str | None): End date.

        Returns:
            list[PostView]: Matching posts.

        Raises:
            AtProtocolError: If request fails.
        """

        params: dict[str, Any] = {}
        try:
            params = {"lang": "en", "q": query, "limit": self.FEED_LIMIT, "sort": "latest"}

            if author:
                params["author"] = author
            if mentions:
                params["mentions"] = mentions
            if tag:
                params["tag"] = tag
            if since:
                params["since"] = since
            if until:
                params["until"] = until

            response = self.blueskyapi.execute_with_retry(
                lambda: self.client.app.bsky.feed.search_posts(params=params), action="retrieving posts"
            )
            logger.info(
                "Retrieved posts",
                query=query,
                author=author,
                mentions=mentions,
                tag=tag,
                since=since,
                until=until,
                limit=self.FEED_LIMIT,
            )
            posts = cast(list[PostView], response.posts)
            return posts

        except AtProtocolError:
            logger.error(
                "Failed to retrieve posts from Bluesky",
                query=query,
                author=author,
                mentions=mentions,
                tag=tag,
                since=since,
                until=until,
            )
            raise

    def post_is_liked_by_x(self, did: str, uri: str, cid: str) -> bool:
        """
        Check if user liked post.

        Parameters:
            did (str): User DID.
            uri (str): Post URI.
            cid (str): Content ID.

        Returns:
            bool: True if liked.

        Raises:
            AtProtocolError: If request fails.
        """

        likes = self.get_likes(uri, cid)
        is_liked = any(like.actor.did == did for like in likes)
        logger.info("Post liked status", is_liked=is_liked, did=did, uri=uri, cid=cid)
        return is_liked

    def post_is_reposted_by_x(self, did: str, uri: str, cid: str) -> bool:
        """
        Check whether a specific user has reposted a given post.

        Args:
            did (str): The decentralized identifier (DID) of the user.
            uri (str): The post URI.
            cid (str): The content ID of the post.

        Returns:
            bool: True if the user has reposted the post, False otherwise.
        """

        reposts = self.get_reposts(uri, cid)
        is_reposted = any(repost.did == did for repost in reposts)
        logger.info("Post reposted status", is_reposted=is_reposted, did=did, uri=uri, cid=cid)
        return is_reposted

    def author_has_posts(self, actor: str) -> bool:
        """
        Check if author has posts.

        Parameters:
            actor (str): User handle or DID.

        Returns:
            bool: True if posts exist.

        Raises:
            AtProtocolError: If request fails.
        """

        feed = self.get_author_feed(actor)
        post_amount = len(feed)
        if post_amount > 0:
            logger.info("Author has posts", actor=actor, post_amount=post_amount, has_posts=True)
            return True
        else:
            logger.info("Author has no posts", actor=actor, post_amount=post_amount, has_posts=False)
            return False

    def author_is_followed_by_x(self, actor: str, did: str) -> bool:
        """
        Check whether a specific user follows a given author.

        Args:
            actor (str): The handle or identifier of the author.
            did (str): The decentralized identifier (DID) of the user.

        Returns:
            bool: True if the user follows the author, False otherwise.
        """

        author_followers = self.get_followers(actor)
        is_followed = any(follower.did == did for follower in author_followers)
        logger.info("Author followed status", is_followed=is_followed, actor=actor, did=did)
        return is_followed
