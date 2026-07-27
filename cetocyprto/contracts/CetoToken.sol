// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

/// @title Ceto Token
/// @notice ERC20 with a rolling mint capacity capped at 20% of supply per window.
contract CetoToken is ERC20, Ownable {
    uint256 public constant ROLLING_BPS = 2000; // 20%
    uint256 public constant BPS_DENOMINATOR = 10_000;
    uint256 public constant ROLLING_WINDOW = 1 days;

    uint256 public windowStart;
    uint256 public mintedInWindow;
    uint256 public windowSupplySnapshot;

    event CapacityWindowReset(uint256 newWindowStart);

    constructor(uint256 initialSupply, address owner_) ERC20("Ceto", "CETO") Ownable(owner_) {
        require(owner_ != address(0), "Owner required");
        windowStart = block.timestamp;
        mintedInWindow = 0;
        windowSupplySnapshot = initialSupply;
        _mint(owner_, initialSupply);
    }

    /// @notice Owner-only mint constrained by the rolling capacity (20% of total supply per window).
    function mint(address to, uint256 amount) external onlyOwner {
        _refreshWindow();
        uint256 limit = rollingLimit();
        require(amount > 0, "Amount zero");
        require(mintedInWindow + amount <= limit, "Rolling capacity exceeded");

        mintedInWindow += amount;
        _mint(to, amount);
    }

    /// @notice Current mintable amount left in the active window.
    function remainingCapacity() external view returns (uint256) {
        uint256 limit = rollingLimit();
        if (block.timestamp >= windowStart + ROLLING_WINDOW) {
            return limit;
        }
        if (limit <= mintedInWindow) {
            return 0;
        }
        return limit - mintedInWindow;
    }

    /// @notice Rolling limit computed as 20% of circulating supply at check time.
    function rollingLimit() public view returns (uint256) {
        return (windowSupplySnapshot * ROLLING_BPS) / BPS_DENOMINATOR;
    }

    function _refreshWindow() internal {
        if (block.timestamp >= windowStart + ROLLING_WINDOW) {
            windowStart = block.timestamp;
            mintedInWindow = 0;
            windowSupplySnapshot = totalSupply();
            emit CapacityWindowReset(windowStart);
        }
    }
}
