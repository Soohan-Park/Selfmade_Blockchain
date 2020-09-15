import sha3 as sha
import time


class Block:
    def __init__(self, _prevBlockHash = "SoohanPark"):
        """
        If the Block is Genesis Block, its _prevBlockHash will be "SoohanPark".
        Else if, the lastest blockHash will be _prevBlockHash.
        """
        # 함수 외에 쓰는 클래스 변수는 클래스가 공유하는 변수
        # self.* 처럼 함수 내에 쓰는 인스턴스는 각 인스턴스 별로 갖게 되는 변수

        # Block Hash
        self.blockHash = None

        # Block Header
        self.prevBlockHash = _prevBlockHash
        self.timeStamp = time.time()
        
        self.isClosed = False

        # Block Body
        self.tx = [] # Transactions's type will be Transaction class.


    def checkClosed(self): # If closed, correction will not allow. (return Flase)
        # if self.isClosed : return False
        # else : return True
        return not(self.isClosed)


    def hashing(self, _target:str):
        """
        _target:str -> str
        """

        return sha.keccak_256(_target.encode("UTF-8")).hexdigest()

    
    def addTx(self, _sender:str, _receiver:str = "", _data:str = ""):
        if self.checkClosed() :
            self.tx.append(Transaction(_sender, _receiver, _data))


    def close(self):
        txListHash = ""
        for t in self.tx:
            txListHash += t.txHash
        txListHash = self.hashing(txListHash)

        data = str(self.prevBlockHash) + str(self.timeStamp) + str(txListHash)
        # make Block Hash.
        self.blockHash = "B" + self.hashing(data)[1:]

        self.isClosed = True

        return self


    def getBlock(self):
        """
        Return dictionary type data.

        For example,
        data = {
            'blockHash' : This is block hash.
            'timeStamp' : ex> '2019-11-18 19:19:28'.
            'tx' : Tx List (-> list).
            'prevBlockHash' : This is prev block hash.
        }
        """

        data = {
            'blockHash' : self.blockHash,
            'timeStamp' : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.timeStamp)),
            'tx' : self.tx,
            
            'prevBlockHash' : self.prevBlockHash
        }
        
        return data


    def getBlockHash(self):
        return self.blockHash


class Transaction:
    def __init__(self, _sender:str, _receiver:str, _data:str):
        # setting
        self.txHash = None
        self.sender = _sender
        self.receiver = _receiver
        self.data = _data # This is str. (only Now | default = "")

        # calc. txHash
        temp = "" + str(_sender) + str(_receiver) + str(time.time()) + str(self.data)

        # make Transaction Hash.
        self.txHash = "T" + self.hashing(temp)[1:]


    def hashing(self, _target:str):
        """
        _target:str -> str
        """

        return sha.keccak_256(_target.encode("UTF-8")).hexdigest()


    def getTx(self):
        """
        Return dictionary type data.

        For example,
        data = {
            'txHash' : This is transaction hash.
            'sender' : Transaction's sender.
            'receiver' : Transaction's receiver.
            'data' : This is data of this Transaction.
        }
        """

        data = {
            'txHash' : self.txHash,
            'sender' : self.sender,
            'receiver' : self.receiver,
            
            'data' : self.data
        }
        
        return data


    def getMessage(self):
        return self.data


    def getTxHash(self):
        return self.txHash