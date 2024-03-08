# [Pimetheus](https://twitter.com/Pimetheus_) - The curious python bot in X space



This is Pimetheus, a bot written in the python programming language.
He is navigating through the X space, traveling on a RaspberryPi Zero.
Shaped by his configuration, he is automated to put into circulation messages defined by his instructions.


![Pimetheus](res/Pimetheus-Image.png)

## Table of Contents

- [Instructions](#Instructions)
- [Requirements](#requirements)
- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [Source code](#source-code)
  - [Blackbox](#blackbox)
- [Contributing](#contributing)
- [License](#license)


## Instructions
Pimetheus instructions ain't rocket science. Every morning, he's starting his journey through X space.
Powered by the Google Search Engine, he is exploring space terms and retrieving relevant Wikipedia results.
On his adventure he's not only tickling his audience with space jokes, but also illuminating them with famous space quotes, 
while constantly controlling the CPU temperature of the RaspberryPi and his travel time.

## Requirements
- Python 3.x
- RaspberryPi
- X Developer account
- Google Developer account

## Getting Started
### Installation

1. [Clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) the repository to your local machine:

    ```bash
    git clone https://github.com/Pymetheus/XBot_Pimetheus
    ```

2. Change into the project directory:

    ```bash
    cd XBot_Pimetheus
    ```
3. Update the API keys in the config.ini

    ```bash
   cd XBot_Pimetheus\.config\config.ini
   ```

### Source Code
The source code of Pimetheus is located in the **src** directory, organized into separate modules.

Discover in **RaspberryPiActions.py** the functions dedicated to fetching CPU temperature, system uptime, and renewing the dhclient.
The **SpaceKeywordList.py** houses three distinct lists: space terms, jokes, and quotes, for the cosmic expedition.
Navigate through **GoogleCustomSearchEngine.py** to exploit the power of custom search queries,
while the APIClient class in **TwitterAPIClient.py** empowers one to unleash messages on X.
**BotActions.py** is where the magic happens, where the RaspberryPi bot comes to life and his actions and interactions are defined.

Lastly, **main.py** serves as mission control, orchestrating the entire operation, utilizing inputs from the SpaceKeywordList to execute specified bot actions.


### Blackbox
The **Blackbox.py**, leveraging the *logging* module, serves as a critical component for Pimetheus safety. 
It is designed to record and store data related to the operation of the bot during his journey through space.

The Blackbox captures a wide range of flight parameters such as initializing methods, returning variable values, capturing exceptions, and various other pieces of information. 
This data is essential for accident investigation, performance analysis, and understanding the sequence of events leading up to an incident or accident.
All gathered information is saved live in [blackbox.log](log/blackbox.log). 

### Contributing
Contributions and co-pilots to this project are welcome! If you would like to contribute, please open an issue to discuss potential changes or submit a pull request.
For more details please visit the [contributing page](docs/CONTRIBUTING.md).

### License

This project is licensed under the [MIT License](LICENSE.md). You are free to use, modify, and distribute this code as permitted by the license.