# CryptoUI
Basic Crypto GUI in Python with PyQt5

Fun Project to learn how to make API calls to Explorers for Wallets and Transactions and CoinGecko for Token Prices.
Supported Chains:
* Ethereum
* Polygon
* Avalanche
* Binance Smart Chain
* Cardano (work in progress)
* Solana (coming soon)

---
## UI Examples

Here is an example of the Tokens and the Transactions from a Specific Wallet on BSC.
![Example - All Transactions](./img/UI%20Examples/Wallet_Transactions.png?raw=true "All Transactions (for Specific Wallet)")

Here we narrow down the transactions for a specific Token (PooCoin for the memes).
![Example - Token Transactions](./img/UI%20Examples/Token_Transactions.png?raw=true "Token Transactions (for Specific Wallet)")

Here we look at the Price History of PooCoin over the last 2 years.
![Example - Price History](./img/UI%20Examples/Token_PriceHistory.png?raw=true "Token Price History")

While the UI is doing an API Call the window is disabled and a waiting animation is triggered to make it nice :)
![Example - API Waiting Animation](./img/UI%20Examples/API_WaitingAnimation.png?raw=true "API Waiting Animation")

---

## TODOs:

### Top 5 Priority
1) Refactor in multiple python files.

### Others
* Add Queue

---

Disclaimer: The code is by no mean perfect. I just thought I would share "as is". Hopefully it can help someone looking to learn and do something similar. 

PS: DO NOT SHARE YOUR API KEYS. (and ideally neither your wallet)