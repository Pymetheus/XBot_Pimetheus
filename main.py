# Main Script
import random
import time
from Blackbox import Blackbox
from SpaceKeywordList import space_terms, space_jokes, space_quotes
from BotActions import create_tweet_information_message, create_tweet_joke_message, create_tweet_quote_message, \
    create_tweet_morning_message, create_tweet_raspi_status_message


blackbox = Blackbox("Main-File")
blackbox_logger = blackbox.logger


if __name__ == '__main__':
    blackbox_logger.info("Initialized MAIN SCRIPT")
    # Setting sleep time between execution
    sleep_time = 7200  # 7200
    rounds_run = 0

    blackbox_logger.info("SCRIPT is activated, start time T-5")
    time.sleep(18000)

    while True:
        # Creating copies from the SpaceKeyword lists
        space_terms_list = space_terms.copy()
        space_jokes_list = space_jokes.copy()
        space_quotes_list = space_quotes.copy()

        rounds_run += 1
        blackbox_logger.info(f"GET: rounds counter: {rounds_run}")
        print(f"\nROUNDS COUNTER: {rounds_run}\n")

        while len(space_jokes_list) > 0:
            start_time = time.time()

            print("MAIN SCRIPT")

            blackbox_logger.info("Initialized 1.MORNING MESSAGE")
            print("\n1.MORNING MESSAGE")
            create_tweet_morning_message()
            time.sleep(sleep_time)

            blackbox_logger.info("Initialized 2.RASPI STATUS")
            print("\n2.RASPI STATUS")
            create_tweet_raspi_status_message()
            time.sleep(sleep_time)

            blackbox_logger.info("Initialized 3.SPACE INFORMATION")
            print("\n3.SPACE INFORMATION")
            message_term = random.choice(space_terms_list)
            create_tweet_information_message(message_term)
            space_terms_list.remove(message_term)
            time.sleep(sleep_time)

            blackbox_logger.info("Initialized 4.RASPI STATUS")
            print("\n4.RASPI STATUS")
            create_tweet_raspi_status_message()
            time.sleep(sleep_time)

            blackbox_logger.info("Initialized 5.SPACE JOKE")
            print("\n5.SPACE JOKE")
            message_joke = random.choice(space_jokes_list)
            create_tweet_joke_message(message_joke)
            space_jokes_list.remove(message_joke)
            time.sleep(sleep_time)

            blackbox_logger.info("Initialized 6.RASPI STATUS")
            print("\n6.RASPI STATUS")
            create_tweet_raspi_status_message()
            time.sleep(sleep_time)

            blackbox_logger.info("Initialized 7.SPACE INFORMATION")
            print("\n7.SPACE INFORMATION")
            message_term = random.choice(space_terms_list)
            create_tweet_information_message(message_term)
            space_terms_list.remove(message_term)
            time.sleep(sleep_time)

            blackbox_logger.info("Initialized 8.RASPI STATUS")
            print("\n8.RASPI STATUS")
            create_tweet_raspi_status_message()
            time.sleep(sleep_time)

            blackbox_logger.info("Initialized 9.SPACE QUOTE")
            print("\n9.SPACE QUOTE")
            message_quot = random.choice(space_quotes_list)
            create_tweet_quote_message(message_quot)
            space_quotes_list.remove(message_quot)
            time.sleep(sleep_time)

            blackbox_logger.info("Initialized 10.RASPI STATUS")
            print("\n10.RASPI STATUS")
            create_tweet_raspi_status_message()
            time.sleep(sleep_time)

            blackbox_logger.info("Initialized 11.SPACE INFORMATION")
            print("\n11.SPACE INFORMATION")
            message_term = random.choice(space_terms_list)
            create_tweet_information_message(message_term)
            space_terms_list.remove(message_term)
            time.sleep(sleep_time)

            blackbox_logger.info("Initialized 12.RASPI STATUS")
            print("\n12.RASPI STATUS")
            create_tweet_raspi_status_message()
            time.sleep(sleep_time)

            end_time = time.time()
            duration = end_time - start_time
            blackbox_logger.info(f"GET duration runtime {duration}")

        blackbox_logger.info(f"GET length of jokes list: {len(space_jokes_list)}")
        blackbox_logger.info(f"GET length of quotes list: {len(space_quotes_list)}")
        blackbox_logger.info(f"GET length of terms list: {len(space_terms_list)}")
