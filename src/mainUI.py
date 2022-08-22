from array import array
import os
import sys
import re
import numpy as np
import pandas as pd
import requests
import datetime
import pytz
from PyQt5 import QtGui
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, QAbstractTableModel
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QLineEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib import dates
from matplotlib.ticker import NullFormatter
import matplotlib.pyplot as plt
import settings

class pandasModel(QAbstractTableModel):

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None

class TabTransactions(QWidget):
    def __init__(self):
        super().__init__()

        self.dfView= QTableView()

        tabLayout = QVBoxLayout()
        tabLayout.addWidget(self.dfView)

        self.setLayout(tabLayout)    
    

class TabPriceHistory(QWidget):
    def __init__(self):
        super().__init__()

        self.figure = plt.figure(facecolor='black')
        self.canvas = FigureCanvas(self.figure)

        self.priceBtn = QPushButton("Price Tx", self)
        self.priceBtn.pressed.connect(self.updatePriceHistoryWithTx)#self.updateBalance)

		# this is the Navigation widget
		# it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        tabLayout = QVBoxLayout()
        tabLayout.addWidget(self.toolbar)
        tabLayout.addWidget(self.canvas)
        tabLayout.addWidget(self.priceBtn)

        self.setLayout(tabLayout)
    
    def updatePriceHistory(self, hdates, hprices):
		# clearing old figure
        self.figure.clear()

		# create an axis
        self.ax = self.figure.add_subplot(111)
        self.ax.plot(hdates, hprices, '-')
        
        self.ax.set_xlim([hdates[0], hdates[-1]])
        self.ax.set_xticks(['2022-07-07', '2021-07-07'])
        self.ax.set_xticklabels(['July', 'July'], rotation=45)
        # formatters' options
        #ax.xaxis.set_major_locator(dates.MonthLocator())
        #ax.xaxis.set_minor_locator(dates.MonthLocator())
        #ax.xaxis.set_major_formatter(dates.DateFormatter('%b'))
        #5ax.xaxis.set_minor_formatter(dates.DateFormatter('%b'))

        self.ax.set_facecolor("black")

		# refresh canvas
        self.canvas.draw()

    def updatePriceHistoryWithTx(self, tdates, tprices):
        self.ax.plot(tdates, tprices, '*')

        self.canvas.draw()

class LoadingAnimation(QWidget):
    def __init__(self):
        super().__init__()

        self.setFixedSize(88,88)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.label_animation = QLabel(self)
        self.movie = QMovie('./img/loading_anim.gif') # LoadingColor2
        self.label_animation.setMovie(self.movie)


    def stopAnimation(self):
        self.movie.stop()
        self.hide()

    def startAnimation(self):
        self.movie.start()
        self.show()


class Window(QWidget):
#class Ui(QtWidgets.QMainWindow):
    # constructor
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("Crypto UI")
        self.setGeometry(300, 250, 900, 600)

        self.loadingAnimation = LoadingAnimation()

        self.walletTxt = QLineEdit()
        self.walletTxt.textChanged.connect(self.changeWallet)

        self.blockchainCB = QComboBox(self)
        self.blockchainCB.addItems(["Ethereum", "Binance (BSC)", "Polygon", "Avalanche", "Solana"])
        self.blockchainCB.activated.connect(self.changeChain)
        self.currencyLabel = QLabel("&Currency:")
        self.currencyLabel.setBuddy(self.blockchainCB)
    
        self.balanceBtn = QPushButton("Balance", self)
        self.balanceBtn.pressed.connect(self.threadedAPI_balance)#self.updateBalance)

        self.tokensBtn = QPushButton("Tokens", self)
        self.tokensBtn.pressed.connect(self.threadedAPI_tokens)#self.updateBalance)

        self.transactionsBtn = QPushButton("Transactions", self)
        self.transactionsBtn.pressed.connect(self.threadedAPI_transactions)

        self.balanceLabel = QLabel("Balance : TBD")

        self.tokensList = QListWidget(self)
        self.tokensList.doubleClicked.connect(self.refreshTransationsForToken)
        self.tokensList.doubleClicked.connect(self.refreshPriceHistoryForToken)

        #self.figure = plt.figure()
        #self.canvas = FigureCanvas(self.figure)

        #self.mySlider = QSlider(Qt.Horizontal, self)
        #self.mySlider.setGeometry(30, 40, 200, 30)
        #self.mySlider.valueChanged[int].connect(self.changeValue)

        self.tabPriceHistory = TabPriceHistory()

        self.tabTransactions = TabTransactions()
        self.tabTransactions.dfView.doubleClicked.connect(self.openTransactionWeb)

        grid = QHBoxLayout()

        btnGrid = QHBoxLayout()
        btnGrid.addWidget(self.balanceBtn)
        btnGrid.addWidget(self.tokensBtn)
        btnGrid.addWidget(self.transactionsBtn)

        subVGrid = QVBoxLayout()
        subVGrid.addWidget(self.walletTxt)
        subVGrid.addWidget(self.currencyLabel)
        subVGrid.addWidget(self.blockchainCB)
        subVGrid.addLayout(btnGrid)
        subVGrid.addWidget(self.balanceLabel)
        subVGrid.addWidget(self.tokensList)
        
        subDFGrid = QVBoxLayout()
        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.tabTransactions, "Transactions")
        self.tabWidget.addTab(self.tabPriceHistory, "Price History")
        subDFGrid.addWidget(self.tabWidget)
        
        grid.addLayout(subVGrid, 3)
        grid.addLayout(subDFGrid, 6)
        
        self.setLayout(grid)

        # Singleton - 1 API owned by the window, not the best design but will do for now.
        self.api = ExplorerAPI(chain='Ethereum')
        self.api.updateBalance.connect(self.updateBalance)
        self.api.updateTokens.connect(self.updateTokens)
        self.api.updateTransactions.connect(self.updateTransactions)

        self.cgapi = CoinGeckoAPI()
        self.cgapi.updatePrices.connect(self.updatePrices)

        self.transactions = None

        self.walletTxt.setText(self.api.getWallet())
        #self.walletTxt.update()

        self.show()

    def changeChain(self, *args):
        self.api.setChain(self.blockchainCB.currentText())

    def changeWallet(self):
        self.api.setWallet(self.walletTxt.text)

    def updateBalance(self, balance):
        self.balanceLabel.setText('Balance: {:.3f}'.format(balance))

        self.loadingAnimation.stopAnimation()
        self.setEnabled(True)

    def updateTokens(self, tokens):
        tokens = sorted(tokens)
        tokens_str = [str(token) for token in tokens]

        #print(tokens)
        self.tokensList.clearSelection()
        self.tokensList.clear()
        self.tokensList.addItems(tokens_str)

        self.loadingAnimation.stopAnimation()
        self.setEnabled(True)

        #self.balanceLabel.setText('You Current Balance on {} is {:.3f}'.format(chain, balance))
    def updateTransactions(self, transactions):
        # Convert to real values (based on Token Decimal)
        qty = [f'{val[:-int(dec)]}.{val[-int(dec):]}' for val,dec in zip(transactions.value, transactions.tokenDecimal)]
        # Keep only 3 decimals.
        qty = [x[:x.rfind('.') + 4] for x in qty]
        # Add a 0 to avoid starting with . (i.e. 0.542 instead of .542)
        qty = [f'0{x}' if x[0]=='.' else x for x in qty]
        transactions['qty'] = qty

        # Convert timestamp to Human DateTime Format.
        transactions['datetime'] = transactions['timeStamp'].apply(lambda x: datetime.datetime.fromtimestamp(int(x)).astimezone(pytz.timezone('America/Montreal')))

        self.transactions = transactions[['datetime', 'tokenSymbol', 'tokenName', 'qty', 'hash']]

        dfmodel = pandasModel(self.transactions)
        self.tabTransactions.dfView.setModel(dfmodel)
        self.tabTransactions.dfView.update()
        self.tabTransactions.dfView.setEnabled(True)

        self.loadingAnimation.stopAnimation()
        self.setEnabled(True)

    def updatePrices(self, prices):
        hprices = [price[1] for price in prices]
        hdates = [datetime.datetime.fromtimestamp(price[0]/1000).strftime('%Y-%m-%d') for price in prices]
        
        self.tabPriceHistory.updatePriceHistory(hdates, hprices)

        self.loadingAnimation.stopAnimation()
        self.setEnabled(True)
        
    def threadedAPI_balance(self):
        self.setEnabled(False)
        self.api.fetchBalance()
        self.loadingAnimation.startAnimation()

    def threadedAPI_tokens(self):
        self.setEnabled(False)
        self.api.fetchTokens()
        self.loadingAnimation.startAnimation()

    def threadedAPI_transactions(self):
        self.setEnabled(False)
        self.api.fetchTransactions()
        self.loadingAnimation.startAnimation()

    def openTransactionWeb(self, index):
        tx_url = f'{self.api.api_explorer}/tx/{index.data()}'
        print(tx_url)
        os.system(f"open \"\" {tx_url}")

    def refreshTransationsForToken(self, index):
        if self.transactions is not None:
            (token_symbol, token_name) = splitTokenInfo(index.data())
            curTransactions = self.transactions[(self.transactions['tokenSymbol'] == token_symbol) & (self.transactions['tokenName'] == token_name)]

            dfmodel = pandasModel(curTransactions)
            self.tabTransactions.dfView.setModel(dfmodel)
            self.tabTransactions.dfView.update()
            self.tabTransactions.dfView.setEnabled(True)

    # Threaded Version.
    def refreshPriceHistoryForToken(self, index):
        self.setEnabled(False)
        self.loadingAnimation.startAnimation()

        (token_symbol, token_name) = splitTokenInfo(index.data())
        processing = self.cgapi.fetchPrice(token_symbol, token_name)
        
        # If the Token isn't on CoinGecko list, no thread API call will launch.
        if not processing:
            self.loadingAnimation.stopAnimation()
            self.setEnabled(True)


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
        print(prices)
        self.updatePrices.emit(prices)

if __name__ == '__main__':
        # creating apyqt5 application
        app = QApplication(sys.argv)
        app.setWindowIcon(QtGui.QIcon('./img/bitcoin_ico.png'))

        # creating a window object
        main = Window()

        # showing the window
        main.show()

        # loop
        sys.exit(app.exec_())


# ------------------------------------------------------
# CURRENTLY DOING
# ------------------------------------------------------
# Adding Transactions to the Price History Graph.
# --> Who's responsible for the TX?
# --> Price History is API threaded, signal-driven.
# --> It's like when the signal arise, then we should check the TX on our way to the UI update...


# TODO To Add Cardano: make Abstract Class "ExplorerAPI()"
# Make classes Implement that Abstract Class.
# - What are the 'Key Functions' such a class should implement?
# - Waht are the 'Key Signals' such a class should "throw"
# Make Ethereum class and then the others derive 'as is' that class.