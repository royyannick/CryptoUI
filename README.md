# CryptoUI
Basic Crypto GUI in Python with PyQt5

Fun Project to learn how to make API calls to Explorers for Wallets and Transactions and CoinGecko for Token Prices.
Supported Chains:
* Ethereum
* Polygon
* Avalanche
* Binance Smart Chain
* Cardano
* Solana (coming soon)

---
## UI Examples

Here is an example of the Tokens and the Transactions from a Specific Wallet on BSC.
![Example - All Transactions](./img/UI%20Examples/Wallet_Transactions.png?raw=true "All Transactions (for Specific Wallet)")

Here we narrow down the transactions for a specific Token (PooCoin for the memes).
![Example - Token Transactions](./img/UI%20Examples/Token_Transactions.png?raw=true "Token Transactions (for Specific Wallet)")

Here we look at the Price History of PooCoin.
![Example - Price History](./img/UI%20Examples/Token_PriceHistory.png?raw=true "Token Price History")

Here we look at the Price History of Cake (Pancake Swap) with the transactions (In/Out).
![Example - Price History and Tx](./img/UI%20Examples/Token_PriceAndTransactions.png?raw=true "Token Price History with Tx")

While the UI is doing an API Call the window is disabled and a waiting animation is triggered to make it nice :)
![Example - API Waiting Animation](./img/UI%20Examples/API_WaitingAnimation.png?raw=true "API Waiting Animation")

---
## How To Use:

1. Clone the Repo.
2. Install PyQt5.
3. Install Matplotlib.
4. Install the requirements (pip install -r requirements.txt, you know the drill).
5. Create a settings.py file in ./src/ with the following constants:
ETHEREUM_EXPLORER_API_KEY = '[INSERT_YOUR_API_KEY]'
POLYGON_EXPLORER_API_KEY = '[INSERT_YOUR_API_KEY]'
AVALANCHE_EXPLORER_API_KEY = '[INSERT_YOUR_API_KEY]'
BSC_EXPLORER_API_KEY = '[INSERT_YOUR_API_KEY]'
CARDANO_EXPLORER_API_KEY = '[INSERT_YOUR_API_KEY]'

WALLET_ETH_MAIN = '[INSERT_YOUR_MAIN_WALLET]'
WALLET_CARDANO_MAIN = '[INSERT_YOUR_MAIN_CARDANO_WALLET]'

---

## TODOs:
* Add Queue for API Calls. (not a priority since the window is disabled for now)
* Small bug in Avax with wETH ? (I have 1 0.995, but should be 0.0995?)
* Speed up Cardano fetching. Can I batch calls and parse after? (maybe fetching all unit ID? how many projects could there be...)

---

Disclaimer: The code is by no mean perfect. I just thought I would share "as is". Hopefully it can help someone looking to learn and do something similar. 

PS: DO NOT SHARE YOUR API KEYS. (and ideally neither your wallet)