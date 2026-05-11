# [Pimetheus](https://bsky.app/profile/pimetheus.bsky.social) - The curious python bot in space

This is Pimetheus, he is currently navigating through the Bluesky space, traveling on a Raspberry Pi.
Shaped by his configuration, he is automated to put messages into circulation defined by his instructions.
Previously home to the X (Twitter) space, he's currently exploring Bluesky.

![Pimetheus](res/Pimetheus-Image.png)


## Table of Contents
- [Instructions](#Instructions)
- [Specifications](#specifications)
  - [Onboard equipment](#onboard-equipment)
  - [Core dependencies](#core-dependencies)
  - [Source code](#source-code)
  - [Black box](#black-box)
- [Contributing](#contributing)
- [License](#license)


## Instructions
Pimetheus instructions ain't rocket science. Every morning, he's starting his journey with a launch message.
While orbiting through the cosmos, he makes several API calls, validates and extracts the data, transforms them into posts and loads them up to space.

**NASA API:**
- Latest Astronomy Picture of the Day (APOD).
- Recent pictures from the Earth Polychromatic Imaging Camera (EPIC).

**Google Search API:**
- Exploring space terms and retrieving relevant Wikipedia results.

**Rocket Launch API:**
- Upcoming orbital rocket launches

On his adventure he's not only sharing space related information with his audience, but also engaging with them through reposts and likes.
Regularly he controls the temperature of his travel device, the Raspberry Pi, and shares it together with his travel time.


## Specifications

### Onboard equipment
- Raspberry Pi
- Bluesky account
- X Developer account
- Google Developer account
- NASA API keys


### Core dependencies
- Python 3.12
- Validation: `pydantic`
- Structured logging: `structlog`
- Http requests: `httpx`
- Image processing: `pillow`
- X API: `tweepy`
- Bluesky API: `atproto`


### Source Code
Pimetheus is built on top of a strict `src/` layout, with the `pyproject.toml` as his center of gravitation.
In the `infrastructure` subdirectory he manages http connections for API calls, image processing, Raspberry Pi interactions and storage handling.
Under the `integrations/apis` subdirectory he fetches, validates and extracts data from various APIs,
whereas under the `integrations/publish` subdirectory he interacts with the Bluesky and X (Twitter) API.
In the `services` subdirectory the bot actions like publishing posts and engagement are managed.

Pimetheus has the following built-in flags:
- **offline**: If True, posting and engagement interactions are only simulated.
- **emulation**: If True, interactions with the Raspberry Pi are emulated.
- **twitter**: If True, posting to X (Twitter) is enabled.
- **bluesky**: If True, posting to Bluesky is enabled.

These flags and other settings are loaded from the configurations file `config.{APP_ENV}.toml`.


### Black box
For his Black box, Pimetheus relies on structured logging, a critical component for learning from accidents and serious incidents during his travels.
All of his actions, flight parameters, system warnings and errors get by default streamed to stdout, but logging to json file can easily be enabled.
This data is essential for accident investigation, performance analysis, and understanding the sequence of events leading up to an incident or accident.

## Cloning
If you want to clone Pimetheus to create your own space traveler powered by a Raspberry Pi follow those steps:

1. Clone the repository to your local machine:

    ```bash
    git clone https://github.com/Pymetheus/Bot_Pimetheus
    ```
2. Replace Pimetheus with your bot name
    ```bash
    cd Bot_Pimetheus
    grep -rl "pimetheus" . | xargs sed -i "s|pimetheus|<your-bot-name>|g"
    mv src/pimetheus "src/<your-bot-name>"
    ```
3. Update the API keys in the env file
    ```bash
    mv .config/.env.example ".config/.env.dev"
    nano .config/.env.dev
    ```


## Contributing
Contributions and co-pilots to this project are welcome! If you would like to contribute, please open an issue to discuss potential changes or submit a pull request.
For more details please visit the [contributing page](docs/CONTRIBUTING.md).

## License

This project is licensed under the [MIT License](LICENSE.md). You are free to use, modify, and distribute this code as permitted by the license.
