import random
import time

import structlog
from atproto_client.models.app.bsky.feed.like import CreateRecordResponse as LikeResponse
from atproto_client.models.app.bsky.feed.repost import CreateRecordResponse as RepostResponse
from atproto_client.models.app.bsky.graph.follow import CreateRecordResponse as FollowResponse

from pimetheus.infrastructure.storage.files import FileStorage
from pimetheus.infrastructure.storage.paths import ProjectPaths
from pimetheus.integrations.publish.bluesky.client import BlueskyAPIClient
from pimetheus.integrations.publish.bluesky.interactor import BlueskyInteractor
from pimetheus.integrations.publish.bluesky.reader import BlueskyReader
from pimetheus.utils.config import Settings
from pimetheus.utils.date_utils import get_date, get_iso_date_from_date

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


class BlueskyEngager:
    """
    Orchestrates engagement actions on BlueSky such as liking, following, and reposting.

    Attributes:
        api (BlueskyAPIClient): Core API client for authentication and retries.
        reader (BlueskyReader): Service for retrieving posts, profiles, and engagement data.
        interactor (BlueskyInteractor): Service for performing actions such as like, follow, and repost.
        bluesky (Any): Bluesky-related configuration from settings.
        bluesky_esa_handles (list[str]): List of ESA-related handles used for engagement.
        bluesky_space_handles (list[str]): List of space-related handles used for engagement.
        engage_timedelta (int): Time window (in days) for filtering recent posts.
        likes_storage (FileStorage): Storage handler for liked posts.
        follows_storage (FileStorage): Storage handler for followed actors.
    """

    settings = Settings.load()
    MIN_SLEEP = 5
    MAX_SLEEP = 15
    MAX_RETRIES = 10

    MIN_LIKES = 1
    MAX_LIKES = 3

    def __init__(self) -> None:
        self.api = BlueskyAPIClient()
        self.reader = BlueskyReader(self.api)
        self.interactor = BlueskyInteractor(self.api)

        self.bluesky = self.settings.pimetheus.bluesky
        self.bluesky_esa_handles = self.settings.bluesky.esa_handles
        self.bluesky_space_handles = self.settings.bluesky.space_handles

        self.engage_timedelta = 14

        self.likes_storage = FileStorage(ProjectPaths.PROCESSED, "bluesky_likes.json")
        self.follows_storage = FileStorage(ProjectPaths.PROCESSED, "bluesky_follows.json")
        self.space_hashtags_storage = FileStorage(ProjectPaths.PROCESSED, "bluesky_space_hashtags.json")

    def sleep_for_random_time(self) -> int:
        """
        Sleep for a random duration to simulate human-like behavior.

        Returns:
            int: Duration of sleep in seconds.
        """

        sleep_time = random.randint(self.MIN_SLEEP, self.MAX_SLEEP)
        logger.info("Sleeping", sleep_time=sleep_time)
        time.sleep(sleep_time)
        return sleep_time

    def get_random_likes_amount(self) -> int:
        """
        Generate a random number of likes to perform.

        Returns:
            int: Number of likes between configured bounds.
        """

        likes_amount = random.randint(self.MIN_LIKES, self.MAX_LIKES)
        logger.info("Like amount", likes_amount=likes_amount)
        return likes_amount

    def get_since_date(self) -> str:
        """
        Get ISO timestamp for the engagement lookback window.

        Returns:
            str: ISO 8601 formatted datetime string.
        """

        date = get_date(self.engage_timedelta)
        date_str = get_iso_date_from_date(date)
        logger.info("Set since date", date_str=date_str)
        return date_str

    def get_random_esa_handle(self) -> str:
        """
        Select a random ESA-related handle from configured list.

        Returns:
            str: Random ESA handle.
        """
        esa_handle = random.choice(self.bluesky_esa_handles)
        logger.info("Selected ESA handle", esa_handle=esa_handle)
        return esa_handle

    def get_random_space_handle(self) -> str:
        """
        Select a random space-related handle from configured list.

        Returns:
            str: Random space-related handle.
        """

        space_handle = random.choice(self.bluesky_space_handles)
        logger.info("Selected space handle", space_handle=space_handle)
        return space_handle

    def get_random_space_hashtag(self) -> str:
        """
        Select a random space-related hashtag from storage.

        Returns:
            str: Random space-related hashtag.
        """
        data: dict[str, list[str]] = {}
        data = self.space_hashtags_storage.read_json()
        random_space_hashtag = random.choice(data["space_hashtags"])
        return random_space_hashtag

    def save_likes_to_json(self, like_dict: dict[int, LikeResponse]) -> None:
        """
        Persist liked post URIs to storage.

        Parameters:
            like_dict (dict[int, LikeResponse]): Mapping of like results.

        Returns:
            None
        """

        stored_likes = self.likes_storage.read_json().get("liked_posts", [])

        for _index, result in like_dict.items():
            like_uri = result.uri

            if like_uri not in stored_likes:
                stored_likes.append(like_uri)

        self.likes_storage.write_json({"liked_posts": stored_likes})
        logger.info("Saved likes to json", stored_likes=stored_likes)

    def save_follows_to_json(self, follows_dict: dict[int, FollowResponse]) -> None:
        """
        Persist followed actor URIs to storage.

        Parameters:
            follows_dict (dict[int, FollowResponse]): Mapping of follow results.

        Returns:
            None
        """

        stored_followers = self.follows_storage.read_json().get("followed_actors", [])

        for _index, result in follows_dict.items():
            follow_uri = result.uri

            if follow_uri not in stored_followers:
                stored_followers.append(follow_uri)

        self.follows_storage.write_json({"followed_actors": stored_followers})
        logger.info("Saved followed actors to json", stored_followers=stored_followers)

    def delete_saved_likes(self) -> None:
        """
        Unlike all previously stored liked posts and clear storage.

        Returns:
            None
        """

        stored_likes = self.likes_storage.read_json().get("liked_posts", [])

        likes = stored_likes.copy()
        for like in likes:
            self.interactor.unlike(like)
            self.sleep_for_random_time()
            stored_likes.remove(like)

        self.likes_storage.write_json({"liked_posts": stored_likes})
        logger.info("Deleted stored likes")

    def delete_saved_follows(self) -> None:
        """
        Unfollow all previously stored followed actors and clear storage.

        Returns:
            None
        """

        stored_followers = self.follows_storage.read_json().get("followed_actors", [])

        followers = stored_followers.copy()
        for follower in followers:
            self.interactor.unfollow(follower)
            self.sleep_for_random_time()
            stored_followers.remove(follower)

        self.follows_storage.write_json({"followed_actors": stored_followers})
        logger.info("Deleted stored followed actors")

    def unengage_likes_and_follows(self) -> None:
        """
        Reverse all previously stored engagement actions.

        Returns:
            None
        """

        self.delete_saved_likes()
        self.delete_saved_follows()
        logger.info("Unengaged likes and follows")

    def like_self_mentioned(self) -> dict[int, LikeResponse]:
        """
        Like recent posts that mention the authenticated user.

        Returns:
            dict[int, LikeResponse]: Mapping of processed index to like responses.
        """

        response_dict: dict[int, LikeResponse] = {}
        posts = self.reader.get_posts(query="*", mentions=self.api.did, since=self.get_since_date())
        if not posts:
            return response_dict
        for index, post in enumerate(posts):
            if not self.reader.post_is_liked_by_x(self.api.did, post.uri, post.cid):
                response = self.interactor.like(uri=post.uri, cid=post.cid)

                if isinstance(response, LikeResponse):
                    response_dict[index] = response
                    logger.info(
                        "Liked self mentioned",
                        response_uri=response.uri,
                        response_cid=response.cid,
                        author=post.author.handle,
                        created_at=post.record.created_at,
                    )
                    self.sleep_for_random_time()
        return response_dict

    def like_random_query_posts_x_times(
        self,
        query: str,
        author: str | None = None,
        mentions: str | None = None,
        tag: list[str] | None = None,
        since: str | None = None,
        until: str | None = None,
        times: int = 1,
    ) -> dict[int, LikeResponse]:
        """
        Like a number of posts matching a search query.

        Parameters:
            query (str): Search query string.
            author (str | None): Filter by author.
            mentions (str | None): Filter by mentions.
            tag (list[str] | None): Hashtag filters.
            since (str | None): Lower bound timestamp (ISO 8601).
            until (str | None): Upper bound timestamp (ISO 8601).
            times (int): Number of posts to like.

        Returns:
            dict[int, LikeResponse]: Mapping of like results.
        """

        response_dict: dict[int, LikeResponse] = {}
        posts = self.reader.get_posts(query=query, author=author, mentions=mentions, tag=tag, since=since, until=until)

        if not posts:
            return response_dict

        rounds = 0
        like_count = 0
        while like_count < times and rounds < self.MAX_RETRIES * times:
            random_post = random.randint(0, len(posts) - 1)
            post_uri = posts[random_post].uri
            post_cid = posts[random_post].cid

            if not self.reader.post_is_liked_by_x(self.api.did, post_uri, post_cid):
                response = self.interactor.like(uri=post_uri, cid=post_cid)

                if isinstance(response, LikeResponse):
                    response_dict[like_count] = response
                    like_count += 1
                    self.sleep_for_random_time()

            rounds += 1
        logger.info("Liked posts", like_count=like_count, rounds=rounds)
        return response_dict

    def like_random_author_posts_x_times(self, actor: str, times: int = 1) -> dict[int, LikeResponse]:
        """
        Like a specified number of random recent posts from a given author.

        Parameters:
            actor (str): Author handle or DID.
            times (int): Number of posts to like.

        Returns:
            dict[int, LikeResponse]: Mapping of like index to responses.
        """

        response_dict: dict[int, LikeResponse] = {}

        if self.reader.author_has_posts(actor):
            feed = self.reader.get_author_feed(actor)
            since_date = self.get_since_date()
            rounds = 0
            like_count = 0
            while like_count < times and rounds < self.MAX_RETRIES * times:
                random_post = random.randint(0, len(feed) - 1)
                post_uri = feed[random_post].post.uri
                post_cid = feed[random_post].post.cid
                post_creation_date = feed[random_post].post.record.created_at

                if since_date < post_creation_date:
                    if not self.reader.post_is_liked_by_x(self.api.did, post_uri, post_cid):
                        response = self.interactor.like(uri=post_uri, cid=post_cid)

                        if isinstance(response, LikeResponse):
                            response_dict[like_count] = response
                            like_count += 1
                            self.sleep_for_random_time()

                rounds += 1

            logger.info("Liked posts", like_count=like_count, rounds=rounds)
            return response_dict
        return response_dict

    def like_random_authors_follower_posts_x_times(self, actor: str, times: int = 1) -> dict[int, LikeResponse]:
        """
        Like posts from randomly selected followers of a given author.

        Parameters:
            actor (str): Author handle or DID.
            times (int): Target number of likes to perform.

        Returns:
            dict[int, LikeResponse]: Mapping of like index to responses.
        """

        logger.info("Liking latest author's followers post", actor=actor, times=times)
        response_dict: dict[int, LikeResponse] = {}
        followers = self.reader.get_followers(actor)

        if not followers:
            return response_dict

        rounds = 0
        remaining_likes = times
        given_likes = 0

        while given_likes < times and rounds < self.MAX_RETRIES * times:
            random_follower = random.randint(0, len(followers) - 1)
            random_actor = followers[random_follower].handle
            result = self.like_random_author_posts_x_times(random_actor, remaining_likes)

            for _key, value in result.items():
                response_dict[len(response_dict)] = value

            given_likes += len(result)
            remaining_likes = times - given_likes
            rounds += 1

        logger.info("Liked posts", given_likes=given_likes, rounds=rounds)
        return response_dict

    def like_random_authors_follows_posts_x_times(self, actor: str, times: int = 1) -> dict[int, LikeResponse]:
        """
        Like posts from randomly selected accounts followed by a given author.

        The method repeatedly selects random followed accounts and attempts to like their posts
        until the desired number of likes is reached or retry limits are exceeded.

        Parameters:
            actor (str): Author handle or DID.
            times (int): Target number of likes to perform.

        Returns:
            dict[int, LikeResponse]: Mapping of like index to responses.
        """

        logger.info("Liking latest author's follows post", actor=actor, times=times)
        response_dict: dict[int, LikeResponse] = {}
        follows = self.reader.get_follows(actor)

        if not follows:
            return response_dict

        rounds = 0
        remaining_likes = times
        given_likes = 0

        while given_likes < times and rounds < self.MAX_RETRIES * times:
            random_follows = random.randint(0, len(follows) - 1)
            random_actor = follows[random_follows].handle
            result = self.like_random_author_posts_x_times(random_actor, remaining_likes)

            for _key, value in result.items():
                response_dict[len(response_dict)] = value

            given_likes += len(result)
            remaining_likes = times - given_likes
            rounds += 1

        logger.info("Liked posts", given_likes=given_likes, rounds=rounds)
        return response_dict

    def repost_latest_esa(self) -> RepostResponse | None:
        """
        Repost the latest ESA post containing media that has not been reposted.

        Returns:
            RepostResponse | None: Repost response if successful, otherwise None.
        """

        logger.info("Reposting latest ESA post")
        feed = self.reader.get_author_feed("esa.int")
        for item in feed:
            if item.post.record.embed:
                post_uri = item.post.uri
                post_cid = item.post.cid

                if not self.reader.post_is_reposted_by_x(self.api.did, post_uri, post_cid):
                    response = self.interactor.repost(uri=post_uri, cid=post_cid)

                    if isinstance(response, RepostResponse):
                        logger.info(
                            "Reposted latest ESA",
                            response_uri=response.uri,
                            response_cid=response.cid,
                            author=item.post.author.handle,
                            created_at=item.post.record.created_at,
                        )
                        self.sleep_for_random_time()
                        return response
        return None

    def follow_random_query_posts_author(
        self,
        query: str,
        author: str | None = None,
        mentions: str | None = None,
        tag: list[str] | None = None,
        since: str | None = None,
        until: str | None = None,
    ) -> dict[int, FollowResponse]:
        """
        Follow the author of a randomly selected post matching search criteria.

        Parameters:
            query (str): Search query string.
            author (str | None): Filter by author.
            mentions (str | None): Filter by mentions.
            tag (list[str] | None): Hashtag filters.
            since (str | None): Lower bound timestamp (ISO 8601).
            until (str | None): Upper bound timestamp (ISO 8601).

        Returns:
            dict[int, FollowResponse]: Mapping of follow results.
        """

        response_dict: dict[int, FollowResponse] = {}
        posts = self.reader.get_posts(query=query, author=author, mentions=mentions, tag=tag, since=since, until=until)

        if not posts:
            return response_dict

        random_post = random.randint(0, len(posts) - 1)
        author_did = posts[random_post].author.did

        if not self.reader.author_is_followed_by_x(actor=author_did, did=self.api.did):
            response = self.interactor.follow(author_did)

            if isinstance(response, FollowResponse):
                response_dict[0] = response
                self.sleep_for_random_time()
        return response_dict
