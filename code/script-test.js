const Web3 = require("web3")

const w3 = new Web3(web3.currentProvider)
window.ethereum.enable()

var address
w3.eth.getAccounts()
.then(accounts => {
    address = accounts[0]
    console.log(address)
})

const contractAddress = "0xb9878c7554Ffd73B6f89cF2C95b4DC2a2aBA0Ba4"
const abi = [ { "constant": false, "inputs": [ { "internalType": "bytes", "name": "time", "type": "bytes" }, { "internalType": "bytes", "name": "temp", "type": "bytes" }, { "internalType": "bytes", "name": "hum", "type": "bytes" } ], "name": "add_records", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "address", "name": "_to", "type": "address" }, { "internalType": "uint8", "name": "color", "type": "uint8" } ], "name": "control_led", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": false, "inputs": [], "name": "destory", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "anonymous": false, "inputs": [ { "indexed": true, "internalType": "address", "name": "_from", "type": "address" }, { "indexed": true, "internalType": "address", "name": "_to", "type": "address" }, { "indexed": false, "internalType": "uint8", "name": "color", "type": "uint8" } ], "name": "led", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": true, "internalType": "address", "name": "_from", "type": "address" }, { "indexed": false, "internalType": "bytes", "name": "time", "type": "bytes" }, { "indexed": false, "internalType": "bytes", "name": "temp", "type": "bytes" }, { "indexed": false, "internalType": "bytes", "name": "hum", "type": "bytes" } ], "name": "records", "type": "event" } ]

const contract = new w3.eth.Contract(abi, contractAddress)

const nodeAddress = document.getElementById("node_address")
const color = document.getElementById("color")

sendTx = function() {
    try {
        contract.methods.control_led(nodeAddress.value, color.value).send({
            from: address
        }).then(receipt => {
            console.log(receipt)
            alert("Successfully sent to Ethereum!")
        })
    } catch(error) {
        alert(error)
    }
}

getData = function() {
    contract.getPastEvents(
        "records", 
        {
            fromBlock: 0,
            toBlock: "latest"
        },
        (err, events) => {
            console.log(events)
            var data = document.getElementById("data")
            data.innerText = ""
            var row = document.createElement("tr")
            var cell1 = document.createElement("td")
            cell1.innerText = "From"
            var cell2 = document.createElement("td")
            cell2.innerText = "Time"
            var cell3 = document.createElement("td")
            cell3.innerText = "Temperature / °C"
            var cell4 = document.createElement("td")
            cell4.innerText = "Humidity / %"
            row.appendChild(cell1)
            row.appendChild(cell2)
            row.appendChild(cell3)
            row.appendChild(cell4)
            data.appendChild(row)
            for (i in events) {
                var event = events[i].returnValues
                var row = document.createElement("tr")
                var cell1 = document.createElement("td")
                cell1.innerText = event._from
                var cell2 = document.createElement("td")
                cell2.innerText = fromHex(event.time)
                var cell3 = document.createElement("td")
                cell3.innerText = fromHex(event.temp)
                var cell4 = document.createElement("td")
                cell4.innerText = fromHex(event.hum)
                row.appendChild(cell1)
                row.appendChild(cell2)
                row.appendChild(cell3)
                row.appendChild(cell4)
                data.appendChild(row)
            }
        }
    )
    
}

function fromHex(hex) {
    var s = ''
    for (var i = 0; i < hex.length; i+=2) {
        s += String.fromCharCode(parseInt(hex.substr(i, 2), 16))
    }
    return decodeURIComponent(escape(s))
}