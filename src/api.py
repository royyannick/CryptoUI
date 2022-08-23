import re
import requests
import pandas as pd
import settings

from PyQt5.QtCore import QObject, pyqtSignal, QThread

class ExplorerAPI(QObject):
    SUPPORTED_CHAINS = ['Ethereum', 'Binance Smart Chain', 'Cardano', 'Avalance', 'Polygon']

    updateBalance = pyqtSignal(float)
    updateTokens = pyqtSignal(list)
    updateTransactions = pyqtSignal(pd.DataFrame)

    class WorkerAPI(QThread):
        finished = pyqtSignal(object)

        def __init__(self, api_url='', parent=None):
            super(QThread, self).__init__()
            self.api_url = api_url

        def run(self):
            print('API [Explorer] Call Requested...')
            response = requests.get(self.api_url)
            print('API [Explorer] Response Received!')
            self.finished.emit(response)

    # constructor
    def __init__(self, parent=None, chain='Ethereum'):
        super().__init__(parent)

        self.chain = ''
        self.setChain(chain)

        self.wallet = settings.WALLET_ETH_MAIN

    # Hook Relay for Balance
    def _responseBalance(self, response):
        balance = float(int(response.json()['result']) * 10**(-1*self.decimal))
        self.updateBalance.emit(balance)

    # Hook Relay for Tokens
    def _responseTokens(self, response):
        df = pd.DataFrame(response.json()['result'])
        tokenList = self.removeTokenDuplicates(df.apply(self.getTokenFromTx, axis=1))
        self.updateTokens.emit(tokenList)

    # Hook Relay for Transactions
    def _responseTransactions(self, response):
        transactions = pd.DataFrame(response.json()['result'])
        self.updateTransactions.emit(transactions)

    # Threaded Function for Balance
    def fetchBalance(self):
        api_url = self.api_url
        api_url = api_url + "?module=account"
        api_url = api_url + "&action=balance"
        api_url = api_url + f"&address={self.wallet}"
        api_url = api_url + f"&apikey={self.api_key}"

        self.thread = QThread()
        self.worker = self.WorkerAPI(api_url=api_url)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        
        self.worker.finished.connect(self._responseBalance)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
    
        self.thread.start()
    
    # Threaded Function for Tokens
    def fetchTokens(self):
        api_url = self.api_url
        api_url = api_url + "?module=account"
        api_url = api_url + "&action=tokentx"
        api_url = api_url + f"&address={self.wallet}"
        api_url = api_url + "&page=1"
        api_url = api_url + "&offset=0"
        api_url = api_url + "&startblock=0"
        api_url = api_url + "&endblock=999999999"
        api_url = api_url + "&sort=asc"
        api_url = api_url + f"&apikey={self.api_key}"

        self.thread = QThread()
        self.worker = self.WorkerAPI(api_url=api_url)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        
        self.worker.finished.connect(self._responseTokens)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
    
        self.thread.start()

    # Threaded Function for Transactions
    def fetchTransactions(self):
        api_url = self.api_url
        api_url = api_url + "?module=account"
        api_url = api_url + "&action=tokentx"
        api_url = api_url + f"&address={self.wallet}"
        api_url = api_url + "&page=1"
        api_url = api_url + "&offset=0"
        api_url = api_url + "&startblock=0"
        api_url = api_url + "&endblock=999999999"
        api_url = api_url + "&sort=asc"
        api_url = api_url + f"&apikey={self.api_key}"

        self.thread = QThread()
        self.worker = self.WorkerAPI(api_url=api_url)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        
        self.worker.finished.connect(self._responseTransactions)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
    
        self.thread.start()

    def getChain(self):
        return self.chain

    def setChain(self, chain):
        self.chain = chain
        print(f'API Chain: {chain}')

        if 'eth' in self.chain.lower():
            self.api_key = settings.ETHEREUM_EXPLORER_API_KEY
            self.api_url = 'https://api.bscscan.com/api'
            self.api_explorer = 'https://bscscan.com'
            self.decimal = 18
        elif 'poly' in self.chain.lower():
            self.api_key = settings.POLYGON_EXPLORER_API_KEY
            self.api_url = 'https://api.polygonscan.com/api'
            self.api_explorer = 'https://polygonscan.com'
            self.decimal = 18
        elif 'ava' in self.chain.lower():
            self.api_key = settings.AVALANCHE_EXPLORER_API_KEY
            self.api_url = 'https://api.snowtrace.io/api'
            self.api_explorer = 'https://snowtrace.io'
            self.decimal = 18
        elif 'bsc' in self.chain.lower() or 'bnb' in self.chain.lower():
            self.api_key = settings.BSC_EXPLORER_API_KEY
            self.api_url = 'https://api.bscscan.com/api'
            self.api_explorer = 'https://bscscan.com'
            self.decimal = 18
        elif 'cardano' in self.chain.lower() or 'bnb' in self.chain.lower():
            self.api_key = settings.CARDANO_EXPLORER_API_KEY
            self.api_url = 'https://cardano-mainnet.blockfrost.io/api/v0'
            self.api_explorer = 'https://cardanoscan.io/'
            self.decimal = 1

    def setWallet(self, wallet):
        if isinstance(wallet, str) and wallet != '':
            self.wallet = wallet
            print(f'API New Wallet: {wallet}')

    def getWallet(self):
        return self.wallet

    def getTokenFromTx(self, tx):
        if 'tokenSymbol' in tx.keys() and 'tokenName' in tx.keys():
            return Token(symbol=tx['tokenSymbol'], name=tx['tokenName'])
        
    def removeTokenDuplicates(self, tokens):
        return [v1 for i, v1 in enumerate(tokens) if not any(v1 == v2 for v2 in tokens[:i])]

class CoinGeckoAPI(QObject):
    updatePrices = pyqtSignal(list)

    class WorkerAPI(QThread):
        finished = pyqtSignal(object)

        def __init__(self, api_url='', parent=None):
            super(QThread, self).__init__()
            self.api_url = api_url

        def run(self):
            print('API [CoinGecko] Call Requested...')
            response = requests.get(self.api_url)
            print('API [CoinGecko] Response Received!')
            self.finished.emit(response)

    def __init__(self):
        super().__init__()
        self.api_url = "https://api.coingecko.com/api/v3/coins/TOKEN/market_chart?vs_currency=usd&days=max"

        print('API [CoinGecko] Fetching Token List...')
        response = requests.get('https://api.coingecko.com/api/v3/coins/list')
        self.tokenList = pd.DataFrame(response.json())
        print('API [CoinGecko] List Received!')

    def fetchPrice(self, tokenSymbol, tokenName):
        processing = False

        tokenID = self.tokenList[(self.tokenList['symbol'] == str.lower(tokenSymbol))]
        if len(tokenID) == 0:
            print(f'--- NO TOKEN FOUND WITH SYMBOL: {tokenSymbol} ---')
        elif len(tokenID) > 1:
            print(f'--- MULTIPLE TOKENS FOUND WITH SYMBOL: {tokenSymbol} ---')
        else:
            tokenID_str = str(tokenID['id'].item())

            self.thread = QThread()
            self.worker = self.WorkerAPI(api_url=self.api_url.replace('TOKEN', tokenID_str))
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            
            self.worker.finished.connect(self._responsePrices)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
    
            self.thread.start()
            processing = True

        return processing

    # Hook Relay for Prices
    def _responsePrices(self, response):
        prices = response.json()['prices']
        #print(prices)
        self.updatePrices.emit(prices)

class Token():
    def __init__(self, symbol, name='N/A', description='N/A', URL='N/A', unit='N/A', decimal=0):
        self.name = name
        self.symbol = symbol
        self.description = description
        self.URL = URL
        self.unit = unit
        self.decimal = decimal

    def __eq__(self, other):
        return self.name == other.name and self.symbol == other.symbol

    def __gt__(self, other):
        return str(self.symbol) > str(other.symbol) 

    def __lt__(self, other):
        return str(self.symbol) < str(other.symbol) 

    def __str__(self):
        return f"{self.symbol} ({self.name})"

    def __repr__(self):
        return f"{self.symbol} ({self.name})"

def splitTokenInfo(tokenStr):
    reg = re.compile(r"(?P<symbol>.*?) \((?P<name>.*?)\)")
    return reg.match(tokenStr).groups()