// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

interface IUniswapV2FactoryLike {
    function getPair(address tokenA, address tokenB) external view returns (address pair);
    function createPair(address tokenA, address tokenB) external returns (address pair);
}

interface IUniswapV2RouterLike {
    function addLiquidity(
        address tokenA,
        address tokenB,
        uint256 amountADesired,
        uint256 amountBDesired,
        uint256 amountAMin,
        uint256 amountBMin,
        address to,
        uint256 deadline
    ) external returns (uint256 amountA, uint256 amountB, uint256 liquidity);
}

interface ITokenFactoryListingRegistry {
    function registerDexListing(
        address tokenAddress,
        address creator,
        address listingTarget,
        address pairAddress
    ) external;
}

/**
 * @title StandardDexLiquidityManager
 * @dev Launch helper that creates a standard AMM pair and adds initial liquidity.
 */
contract StandardDexLiquidityManager is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    address public immutable baseToken;
    address public dexRouter;
    address public dexFactory;
    address public listingRegistry;

    event DexConfigUpdated(address indexed router, address indexed factory);
    event ListingRegistryUpdated(address indexed registry);
    event TokenLaunched(
        address indexed creator,
        address indexed token,
        address indexed pair,
        uint256 tokenAmount,
        uint256 baseAmount,
        uint256 liquidity
    );

    constructor(
        address _baseToken,
        address _dexRouter,
        address _dexFactory,
        address _listingRegistry
    ) Ownable(msg.sender) {
        require(_baseToken != address(0), "Invalid base token");
        require(_dexRouter != address(0), "Invalid router");
        require(_dexFactory != address(0), "Invalid factory");
        require(_listingRegistry != address(0), "Invalid registry");

        baseToken = _baseToken;
        dexRouter = _dexRouter;
        dexFactory = _dexFactory;
        listingRegistry = _listingRegistry;
    }

    function setDexConfig(address newRouter, address newFactory) external onlyOwner {
        require(newRouter != address(0), "Invalid router");
        require(newFactory != address(0), "Invalid factory");
        dexRouter = newRouter;
        dexFactory = newFactory;
        emit DexConfigUpdated(newRouter, newFactory);
    }

    function setListingRegistry(address newRegistry) external onlyOwner {
        require(newRegistry != address(0), "Invalid registry");
        listingRegistry = newRegistry;
        emit ListingRegistryUpdated(newRegistry);
    }

    function launchToken(
        address token,
        uint256 tokenAmountDesired,
        uint256 baseAmountDesired,
        uint256 amountTokenMin,
        uint256 amountBaseMin,
        uint256 deadline
    )
        external
        nonReentrant
        returns (
            address pair,
            uint256 amountToken,
            uint256 amountBase,
            uint256 liquidity
        )
    {
        require(token != address(0) && token != baseToken, "Invalid token");
        require(tokenAmountDesired > 0 && baseAmountDesired > 0, "Invalid amounts");

        IERC20(token).safeTransferFrom(msg.sender, address(this), tokenAmountDesired);
        IERC20(baseToken).safeTransferFrom(msg.sender, address(this), baseAmountDesired);

        pair = IUniswapV2FactoryLike(dexFactory).getPair(token, baseToken);
        if (pair == address(0)) {
            pair = IUniswapV2FactoryLike(dexFactory).createPair(token, baseToken);
        }

        _resetAndApprove(token, dexRouter, tokenAmountDesired);
        _resetAndApprove(baseToken, dexRouter, baseAmountDesired);

        (amountToken, amountBase, liquidity) = IUniswapV2RouterLike(dexRouter).addLiquidity(
            token,
            baseToken,
            tokenAmountDesired,
            baseAmountDesired,
            amountTokenMin,
            amountBaseMin,
            msg.sender,
            deadline
        );

        _resetAndApprove(token, dexRouter, 0);
        _resetAndApprove(baseToken, dexRouter, 0);

        if (tokenAmountDesired > amountToken) {
            IERC20(token).safeTransfer(msg.sender, tokenAmountDesired - amountToken);
        }

        if (baseAmountDesired > amountBase) {
            IERC20(baseToken).safeTransfer(msg.sender, baseAmountDesired - amountBase);
        }

        ITokenFactoryListingRegistry(listingRegistry).registerDexListing(
            token,
            msg.sender,
            dexRouter,
            pair
        );

        emit TokenLaunched(msg.sender, token, pair, amountToken, amountBase, liquidity);
    }

    function previewPair(address token) external view returns (address pair) {
        return IUniswapV2FactoryLike(dexFactory).getPair(token, baseToken);
    }

    function _resetAndApprove(address token, address spender, uint256 amount) internal {
        IERC20(token).forceApprove(spender, amount);
    }
}
