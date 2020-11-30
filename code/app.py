import json
import time
import board
import adafruit_dht
from web3 import Web3
from gpiozero import Button, RGBLED
from web3.gas_strategies.time_based import (fast_gas_price_strategy,
											medium_gas_price_strategy,
											slow_gas_price_strategy,
											glacial_gas_price_strategy)

def main():
	print("=============================================================================")

	infura_url = "https://ropsten.infura.io/v3/e08b40808f684eb19d87cc56a1effb58"
	w3 = Web3(Web3.HTTPProvider(infura_url))
	if w3.isConnected():
		print("Successfully connected to Infura")
	else:
		print("Failed to connect to Infura, please check your network")
		return

	button = Button(2)
	sensor = adafruit_dht.DHT22(board.D14)
	codes = ((0,0,0),(0,0,1),(0,1,0),(0,1,1),(1,0,0),(1,0,1),(1,1,0),(1,1,1))
	colors = ("off","blue","red","cyan","green","magenta","yellow","white")
	led = RGBLED(red=9, green=10, blue=11)
	led.color = codes[7]
	print("The initial led color is white")

	print("Setting gas price strategy. Please wait...")
	w3.eth.setGasPriceStrategy(fast_gas_price_strategy)
	gas_price = w3.eth.generateGasPrice()
	print("Estimated gas price {} gwei".format(Web3.fromWei(gas_price, "gwei")))

	contract_address = "0xb9878c7554Ffd73B6f89cF2C95b4DC2a2aBA0Ba4"
	abi = json.loads('[ { "constant": false, "inputs": [ { "internalType": "bytes", "name": "time", "type": "bytes" }, { "internalType": "bytes", "name": "temp", "type": "bytes" }, { "internalType": "bytes", "name": "hum", "type": "bytes" } ], "name": "add_records", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": false, "inputs": [ { "internalType": "address", "name": "_to", "type": "address" }, { "internalType": "uint8", "name": "color", "type": "uint8" } ], "name": "control_led", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "constant": false, "inputs": [], "name": "destory", "outputs": [], "payable": false, "stateMutability": "nonpayable", "type": "function" }, { "anonymous": false, "inputs": [ { "indexed": true, "internalType": "address", "name": "_from", "type": "address" }, { "indexed": true, "internalType": "address", "name": "_to", "type": "address" }, { "indexed": false, "internalType": "uint8", "name": "color", "type": "uint8" } ], "name": "led", "type": "event" }, { "anonymous": false, "inputs": [ { "indexed": true, "internalType": "address", "name": "_from", "type": "address" }, { "indexed": false, "internalType": "bytes", "name": "time", "type": "bytes" }, { "indexed": false, "internalType": "bytes", "name": "temp", "type": "bytes" }, { "indexed": false, "internalType": "bytes", "name": "hum", "type": "bytes" } ], "name": "records", "type": "event" } ]')
	account_address = "0x89271f3D30A6C5c7B29df718D00d93c924e58D1F"
	private_key = "7106B9FA0663727B1DEC493FE77DC4F303614F0E2D62EE527FC8A4AFB463463E"

	contract = w3.eth.contract(address=contract_address, abi=abi)
	event_filter = contract.events.led.createFilter(fromBlock="latest", argument_filters={"_to": account_address})
	
	print("=============================================================================")

	def encode(x):
		return str(x).encode()

	def send_tx():
		try:
			timestamp = time.asctime()
			temperature = sensor.temperature
			humidity = sensor.humidity
			print("{}	Temperature:{}C	Humidity:{}%".format(timestamp, temperature, humidity))
			print("-----------------------------------------------------------------------------")

		except RuntimeError as error:
			print("Failed to get temperature and humidity. Please try again...")
			print(error)
			print("=============================================================================")
			return

		timestamp_encode = encode(timestamp)
		temperature_encode = encode(temperature)
		humidity_encode = encode(humidity)
		nonce = w3.eth.getTransactionCount(account_address)
		function = contract.functions.add_records(timestamp_encode, temperature_encode, humidity_encode)
		tx = function.buildTransaction({"nonce": nonce})
		print("Transaction:")
		print(tx)
		print("-----------------------------------------------------------------------------")
		
		try:
			signed_tx = w3.eth.account.signTransaction(tx, private_key)
			tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
			receipt = w3.eth.waitForTransactionReceipt(tx_hash)
			print("Successfully sent to Ethereum")
			print("gas used:", receipt.cumulativeGasUsed)
			print("contract address:", contract_address)
			print("tx:", Web3.toHex(receipt.transactionHash))
			print("block:", Web3.toHex(receipt.blockHash))
		except Exception as e:
			print(e)
		print("=============================================================================")

	while True:
		for event in event_filter.get_new_entries():
			color = event.args.color
			print("Changed led color to", colors[color])
			led.color = codes[color]
			print("from:", event.args._from)
			print("tx:", Web3.toHex(event.transactionHash))
			print("block:", Web3.toHex(event.blockHash))
			print("=============================================================================")
		
		button.when_pressed = send_tx
		time.sleep(1)


if __name__ == "__main__":
    main()










