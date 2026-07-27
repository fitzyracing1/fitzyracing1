// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract UniswapV2PairMock is ERC20 {
    address public token0;
    address public token1;

    constructor(address _token0, address _token1) ERC20("Mock LP Token", "MLP") {
        token0 = _token0;
        token1 = _token1;
    }

    function mint(address to, uint256 amount) external {
        _mint(to, amount);
    }
}

contract UniswapV2FactoryMock {
    mapping(address => mapping(address => address)) public getPair;

    function createPair(address tokenA, address tokenB) external returns (address pair) {
        require(tokenA != tokenB, "Identical addresses");
        require(getPair[tokenA][tokenB] == address(0), "Pair exists");

        UniswapV2PairMock newPair = new UniswapV2PairMock(tokenA, tokenB);
        pair = address(newPair);

        getPair[tokenA][tokenB] = pair;
        getPair[tokenB][tokenA] = pair;
    }
}

contract UniswapV2RouterMock {
    address public immutable factory;

    constructor(address factoryAddress) {
        factory = factoryAddress;
    }

    function addLiquidity(
        address tokenA,
        address tokenB,
        uint256 amountADesired,
        uint256 amountBDesired,
        uint256 amountAMin,
        uint256 amountBMin,
        address to,
        uint256
    ) external returns (uint256 amountA, uint256 amountB, uint256 liquidity) {
        require(amountADesired >= amountAMin, "Insufficient A");
        require(amountBDesired >= amountBMin, "Insufficient B");

        address pair = UniswapV2FactoryMock(factory).getPair(tokenA, tokenB);
        require(pair != address(0), "Pair missing");

        amountA = amountADesired;
        amountB = amountBDesired;

        IERC20(tokenA).transferFrom(msg.sender, pair, amountA);
        IERC20(tokenB).transferFrom(msg.sender, pair, amountB);

        liquidity = _sqrt(amountA * amountB);
        UniswapV2PairMock(pair).mint(to, liquidity);
    }

    function _sqrt(uint256 y) internal pure returns (uint256 z) {
        if (y > 3) {
            z = y;
            uint256 x = y / 2 + 1;
            while (x < z) {
                z = x;
                x = (y / x + x) / 2;
            }
        } else if (y != 0) {
            z = 1;
        }
    }
}
