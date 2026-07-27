// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract AttentionToken is ERC20, ERC20Burnable, Ownable {
    uint256 public immutable cap;
    mapping(address => bool) public isMinter;

    event MinterUpdated(address indexed account, bool allowed);

    constructor(
        string memory name_,
        string memory symbol_,
        uint256 cap_,
        address initialOwner
    ) ERC20(name_, symbol_) Ownable(initialOwner) {
        require(cap_ > 0, "Cap must be > 0");
        cap = cap_;
    }

    modifier onlyMinter() {
        require(isMinter[msg.sender], "Not minter");
        _;
    }

    function setMinter(address account, bool allowed) external onlyOwner {
        require(account != address(0), "Invalid account");
        isMinter[account] = allowed;
        emit MinterUpdated(account, allowed);
    }

    function mint(address to, uint256 amount) external onlyMinter {
        require(totalSupply() + amount <= cap, "Cap exceeded");
        _mint(to, amount);
    }
}
