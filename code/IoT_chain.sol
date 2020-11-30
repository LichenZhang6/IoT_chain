pragma solidity >=0.4.22 <0.6.0;

contract owned {
    address owner;

    constructor() internal {
        owner = msg.sender;
    }

    modifier onlyOwner {
        require(msg.sender == owner);
        _;
    }
}

contract mortal is owned {
    function destory() public onlyOwner {
        selfdestruct(msg.sender);
    }
}

contract IoT_chain is mortal {
    event records(address indexed _from, bytes time, bytes temp, bytes hum);
    event led(address indexed _from, address indexed _to, uint8 color);

    function add_records(
        bytes memory time,
        bytes memory temp,
        bytes memory hum
    ) public {
        emit records(msg.sender, time, temp, hum);
    }

    function control_led(address _to, uint8 color) public {
        emit led(msg.sender, _to, color);
    }
}
