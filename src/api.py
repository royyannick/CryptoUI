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

    # constructor
    def __init__(self, parent=None, chain='Ethereum'):
        super().__init__()

        self.api_eth = ExplorerAPI_Eth(chain='Ethereum')
        self.api_cardano = ExplorerAPI_Cardano()

        self.api_eth.updateBalance.connect(self._responseBalance)
        self.api_eth.updateTokens.connect(self._responseTokens)
        self.api_eth.updateTransactions.connect(self._responseTransactions)
        self.api_cardano.updateBalance.connect(self._responseBalance)
        self.api_cardano.updateTokens.connect(self._responseTokens)
        self.api_cardano.updateTransactions.connect(self._responseTransactions)

        self.chain = ''
        self.setChain(chain)

        self.wallet = settings.WALLET_ETH_MAIN

    # Hook Relay for Balance
    def _responseBalance(self, balance):
        self.updateBalance.emit(balance)

    # Hook Relay for Tokens
    def _responseTokens(self, tokenList):
        self.updateTokens.emit(tokenList)

    # Hook Relay for Transactions
    def _responseTransactions(self, transactions):
        self.updateTransactions.emit(transactions)

    #@abstractmethod
    def fetchBalance(self):
        if self.chain.lower() == 'cardano':
            self.api_cardano.fetchBalance()
        else:
            self.api_eth.fetchBalance()

    #@abstractmethod
    def fetchTokens(self):
        if self.chain.lower() == 'cardano':
            self.api_cardano.fetchTokens()
        else:
            self.api_eth.fetchTokens()

    #@abstractmethod
    def fetchTransactions(self):
        if self.chain.lower() == 'cardano':
            self.api_cardano.fetchTransactions()
        else:
            self.api_eth.fetchTransactions()

    def getChain(self):
        return self.chain

    def setChain(self, chain):
        self.chain = chain
        if chain.lower() != 'cardano':
            self.api_eth.setChain(chain)
    
    def setWallet(self, wallet):
        self.api_cardano.setWallet(wallet)
        self.api_eth.setWallet(wallet)

    def getWallet(self):
        return self.wallet

    def getExplorer(self):
        if self.chain.lower() != 'cardano':
            return self.api_eth.api_explorer
        else:
            return self.api_cardano.api_explorer
    

class ExplorerAPI_Eth(QObject):
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
    def __init__(self, chain='Ethereum'):
        super().__init__()

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


class ExplorerAPI_Cardano(QObject):
    updateBalance = pyqtSignal(float)
    updateTokens = pyqtSignal(list)
    updateTransactions = pyqtSignal(pd.DataFrame)

    class WorkerAPI(QThread):
        finished = pyqtSignal(object)

        def __init__(self, api_url='', parent=None):
            super(QThread, self).__init__()
            self.api_url = api_url

        def run(self):
            print('API [Explorer] (Cardano) Call Requested...')
            response = requests.get(self.api_url, headers={'project_id':settings.CARDANO_EXPLORER_API_KEY})
            print('API [Explorer] (Cardano) Response Received!')
            self.finished.emit(response)

        # constructor
    def __init__(self):
        super().__init__()

        self.api_key = settings.CARDANO_EXPLORER_API_KEY
        self.api_url = 'https://cardano-mainnet.blockfrost.io/api/v0/'
        self.api_explorer = 'https://cardanoscan.io'
        self.decimal = 6
        self.wallet = settings.WALLET_CARDANO_MAIN

    # Hook Relay for Balance
    def _responseBalance(self, response):
        balance = 0
        account = response.json()
        for token in account['amount']:
            if token['unit'] == 'lovelace': # ADA unit name
                balance = int(token['quantity']) * 10**(-1 * self.decimal)
        self.updateBalance.emit(balance)

    # Hook Relay for Tokens
    def _responseTokens(self, response):
        account = response.json()
        tokenList = []

        for token in account['amount']:
            response = requests.get(f"{self.api_url}assets/{token['unit']}", headers={'project_id':self.api_key})
            if int(response.status_code) == 200:
                asset = response.json()

                if asset['metadata'] is not None:
                    #print(f"Ticker: {asset['metadata']['ticker']} | Name: {asset['metadata']['name']} = {token['quantity']} ({asset['metadata']['decimals']})")
                    qty = int(token['quantity']) * 10**(-1 *(int(asset['metadata']['decimals'])))
                    #print(f">> Quantity = {qty}")
                    tokenList.append(Token(symbol=asset['metadata']['ticker'], name=asset['metadata']['name']))
                else:
                    print(f"Skipping: {asset['asset']}")
            else:
                print(f"Skipping: {token['unit']}")

        self.updateTokens.emit(tokenList)

    def getTokenFromTx(self, tx):
        if 'tokenSymbol' in tx.keys() and 'tokenName' in tx.keys():
            return Token(symbol=tx['tokenSymbol'], name=tx['tokenName'])

    # Hook Relay for Transactions
    def _responseTransactions(self, response):
        txs = response.json()
        txList = []
        #print(transactions)

        for tx in txs:
            #response = requests.get(f"{self.api_url}txs/{tx['tx_hash']}", headers={'project_id':self.api_key})
            #transaction = response.json()

            #print("-------------------------")
            #print(transaction)
            #print("-------------------------")

            txList.append(tx['tx_hash'])

        transactions = pd.DataFrame(txList, columns=['Hash'])
        self.updateTransactions.emit(transactions)

    # Threaded Function for Balance
    def fetchBalance(self):
        api_url = self.api_url
        api_url = api_url + "addresses/"
        api_url = api_url + f"{self.wallet}"

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
        api_url = api_url + "addresses/"
        api_url = api_url + f"{self.wallet}"

        print(api_url)

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
        api_url = api_url + "addresses/"
        api_url = api_url + f"{self.wallet}"
        api_url = api_url + "/transactions?order=desc"

        self.thread = QThread()
        self.worker = self.WorkerAPI(api_url=api_url)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        
        self.worker.finished.connect(self._responseTransactions)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
    
        self.thread.start()

    def setWallet(self, wallet):
        pass
        #if isinstance(wallet, str) and wallet != '':
        #    self.wallet = wallet
        #    print(f'API New Wallet: {wallet}')

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