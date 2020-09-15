from models import block
import uuid
import threading
import time
import requests
import sha3 as sha
from flask import Flask, redirect, render_template, json, request


chain = []
nodes = set() # 합의 과정을 위한 노드의 집합.
curr = None

UUID = sha.keccak_256(str(uuid.uuid4()).encode('UTF-8')).hexdigest()
app = Flask(__name__)


def main():
    global curr

    flag = True
    curr = block.Block() # make Genesis Block.

    # Thread for closing Block.
    geneCycleTime = 10
    t = threading.Thread(target=close, args=(geneCycleTime, ))
    t.daemon = True
    t.start()

    # Run Web-App.
    app.run(0)


@app.route('/')
def index():
    global chain
    try:
        chainLength = len(chain)
        lastGeneTime = chain[chainLength-1].getBlock()['timeStamp']
    except IndexError as err:
        time.sleep(5)
        chainLength = len(chain)
        lastGeneTime = chain[chainLength-1].getBlock()['timeStamp']

    return render_template('index.html', chainLength=chainLength, lastGeneTime=lastGeneTime)


@app.route('/addtx')
def addTx():
    global chain, UUID

    chainLength = len(chain)

    return render_template('addtx.html', chainLength=chainLength, sender=UUID)


@app.route('/adding', methods=['POST'])
def adding():
    global curr, UUID, chain

    sender = UUID
    receiver = request.form['receiver']
    message = request.form['message']

    curr.addTx(_sender=sender, _receiver=receiver, _data=message)

    return "<script>alert('Success'); location.href='/chain';</script>"


@app.route('/block/<i>')
def getBlock(i):
    global curr, chain

    temp = chain[int(i)].getBlock()
    
    blockHash = temp['blockHash']
    prevBlockHash = temp['prevBlockHash']
    timeStamp = temp['timeStamp']
    txs = [t.getTx() for t in temp['tx'] ] # Instance of Transaction. | The elements are typed Dict.
    txsLength = len(txs)

    return render_template("block_info.html", blockHash=blockHash, prevBlockHash=prevBlockHash, timeStamp=timeStamp, txs=txs, txsLength=txsLength)


@app.route('/tx/<txHash>') # /tx/<tx or block#> 으로 수정할 것
def getTx(txHash):
    global chain
    
    for i in range(len(chain)):
            temp = chain[i].getBlock()['tx']
            if len(temp) != 0:
                for t in temp:
                    if txHash == t.getTxHash():
                        temp = t.getTx()
                        sender = temp['sender']
                        receiver = temp['receiver']
                        message = temp['data']
                        break
    return render_template("tx_info.html", txHash=txHash, sender=sender, receiver=receiver, message=message)


@app.route('/chain')
def getChain():
    global chain
    
    chainLength = len(chain)

    j = []
    for i in range(chainLength):
        j.append(chain[i].getBlock())

    return render_template('chain.html', j=j, chainLength=chainLength)


@app.route('/search', methods=['POST'])
def search():
    global chain

    keyword = str(request.form['keyword'])

    if keyword == "":
        return errorMsgBack('Please input the keyword.')


    elif keyword.isnumeric(): # Block #
        if len(chain) <= int(keyword):
            return errorMsgBack('The block number is not found.')
        
        return redirect('/block/{}'.format(keyword))


    elif keyword[0] == "B": # Block Hash
        blockNum = None
        for i in range(len(chain)):
            if keyword == chain[i].getBlockHash():
                blockNum = i
                break
        
        if blockNum is None:
            return errorMsgBack('The blockHash is not found.')

        return redirect('/block/{}'.format(blockNum))


    elif keyword[0] == "T": # Transaction Hash
        txHash = None
        for i in range(len(chain)):
            temp = chain[i].getBlock()['tx']
            if len(temp) != 0:
                for t in temp:
                    if keyword == t.getTxHash():
                        txHash = t.getTxHash()
                        break
        
        if txHash is None:
            return errorMsgBack('The txHash is not found.')

        return redirect('/tx/{}'.format(txHash))


    elif keyword in ("genesis", "Genesis", "GENESIS"):
        return redirect('/block/0')


    else:
        return errorMsgBack('Unknown error. Please try again.')


def close(_geneCycleTime):
    global chain, curr

    while True:
        # Cycle time of Block Generation.
        time.sleep(_geneCycleTime)

        chain.append(curr.close())
        lastBlockHash = curr.getBlockHash()
        
        curr = block.Block(lastBlockHash) # open new Block.


def errorMsgBack(msg:str):
    """
    Input the error message, this function will make the error alert & history.back script.\n
    The script type is String. (str -> str)
    """
    return "<script>alert('{}'); history.back();</script>".format(msg)


if __name__ == '__main__':
    main()