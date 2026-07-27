// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title MemeDex
 * @dev Multi-pair DEX for meme tokens with automatic liquidity pools
 */
contract MemeDex is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;
    
    struct Pool {
        uint256 token0Reserve;
        uint256 token1Reserve;
        uint256 totalLiquidity;
        mapping(address => uint256) liquidity;
        bool exists;
    }
    
    // Base token (USDC or similar)
    address public baseToken;
    
    // Trading fee (0.3% = 30 basis points)
    uint256 public constant FEE_BASIS_POINTS = 30;
    uint256 public constant BASIS_POINTS = 10000;
    
    // Protocol fee recipient
    address public feeRecipient;
    
    // Pool for each token paired with base token
    // token => Pool
    mapping(address => Pool) public pools;
    
    // All tokens with pools
    address[] public allTokens;
    
    // Minimum liquidity locked forever
    uint256 public constant MINIMUM_LIQUIDITY = 1000;
    
    // Events
    event PoolCreated(
        address indexed token,
        address indexed baseToken,
        uint256 tokenAmount,
        uint256 baseAmount,
        address indexed creator
    );
    
    event LiquidityAdded(
        address indexed token,
        address indexed provider,
        uint256 tokenAmount,
        uint256 baseAmount,
        uint256 liquidity
    );
    
    event LiquidityRemoved(
        address indexed token,
        address indexed provider,
        uint256 tokenAmount,
        uint256 baseAmount,
        uint256 liquidity
    );
    
    event Swap(
        address indexed user,
        address indexed tokenIn,
        address indexed tokenOut,
        uint256 amountIn,
        uint256 amountOut,
        uint256 fee
    );
    
    constructor(address _baseToken, address _feeRecipient) Ownable(msg.sender) {
        require(_baseToken != address(0), "Invalid base token");
        require(_feeRecipient != address(0), "Invalid fee recipient");
        
        baseToken = _baseToken;
        feeRecipient = _feeRecipient;
    }
    
    /**
     * @dev Create a new liquidity pool for a token
     */
    function createPool(
        address token,
        uint256 tokenAmount,
        uint256 baseAmount
    ) external nonReentrant returns (uint256 liquidity) {
        require(token != address(0) && token != baseToken, "Invalid token");
        require(!pools[token].exists, "Pool already exists");
        require(tokenAmount > 0 && baseAmount > 0, "Invalid amounts");
        
        // Transfer tokens
        IERC20(token).safeTransferFrom(msg.sender, address(this), tokenAmount);
        IERC20(baseToken).safeTransferFrom(msg.sender, address(this), baseAmount);
        
        // Initialize pool
        Pool storage pool = pools[token];
        pool.exists = true;
        pool.token0Reserve = tokenAmount;
        pool.token1Reserve = baseAmount;
        
        // Calculate initial liquidity (geometric mean)
        liquidity = _sqrt(tokenAmount * baseAmount);
        require(liquidity > MINIMUM_LIQUIDITY, "Insufficient liquidity");
        
        // Lock minimum liquidity forever
        pool.totalLiquidity = liquidity;
        pool.liquidity[address(0)] = MINIMUM_LIQUIDITY;
        pool.liquidity[msg.sender] = liquidity - MINIMUM_LIQUIDITY;
        
        allTokens.push(token);
        
        emit PoolCreated(token, baseToken, tokenAmount, baseAmount, msg.sender);
        emit LiquidityAdded(token, msg.sender, tokenAmount, baseAmount, liquidity - MINIMUM_LIQUIDITY);
        
        return liquidity - MINIMUM_LIQUIDITY;
    }
    
    /**
     * @dev Add liquidity to existing pool
     */
    function addLiquidity(
        address token,
        uint256 tokenAmount,
        uint256 baseAmount,
        uint256 minLiquidity
    ) external nonReentrant returns (uint256 liquidity) {
        Pool storage pool = pools[token];
        require(pool.exists, "Pool does not exist");
        require(tokenAmount > 0 && baseAmount > 0, "Invalid amounts");
        
        // Calculate optimal amounts based on current ratio
        uint256 optimalBaseAmount = (tokenAmount * pool.token1Reserve) / pool.token0Reserve;
        
        if (optimalBaseAmount <= baseAmount) {
            baseAmount = optimalBaseAmount;
        } else {
            tokenAmount = (baseAmount * pool.token0Reserve) / pool.token1Reserve;
        }
        
        // Transfer tokens
        IERC20(token).safeTransferFrom(msg.sender, address(this), tokenAmount);
        IERC20(baseToken).safeTransferFrom(msg.sender, address(this), baseAmount);
        
        // Calculate liquidity to mint
        liquidity = (tokenAmount * pool.totalLiquidity) / pool.token0Reserve;
        require(liquidity >= minLiquidity, "Slippage too high");
        
        // Update pool
        pool.token0Reserve += tokenAmount;
        pool.token1Reserve += baseAmount;
        pool.totalLiquidity += liquidity;
        pool.liquidity[msg.sender] += liquidity;
        
        emit LiquidityAdded(token, msg.sender, tokenAmount, baseAmount, liquidity);
        
        return liquidity;
    }
    
    /**
     * @dev Remove liquidity from pool
     */
    function removeLiquidity(
        address token,
        uint256 liquidity,
        uint256 minTokenAmount,
        uint256 minBaseAmount
    ) external nonReentrant returns (uint256 tokenAmount, uint256 baseAmount) {
        Pool storage pool = pools[token];
        require(pool.exists, "Pool does not exist");
        require(liquidity > 0, "Invalid liquidity");
        require(pool.liquidity[msg.sender] >= liquidity, "Insufficient liquidity");
        
        // Calculate amounts to return
        tokenAmount = (liquidity * pool.token0Reserve) / pool.totalLiquidity;
        baseAmount = (liquidity * pool.token1Reserve) / pool.totalLiquidity;
        
        require(tokenAmount >= minTokenAmount, "Slippage: token amount too low");
        require(baseAmount >= minBaseAmount, "Slippage: base amount too low");
        
        // Update pool
        pool.token0Reserve -= tokenAmount;
        pool.token1Reserve -= baseAmount;
        pool.totalLiquidity -= liquidity;
        pool.liquidity[msg.sender] -= liquidity;
        
        // Transfer tokens
        IERC20(token).safeTransfer(msg.sender, tokenAmount);
        IERC20(baseToken).safeTransfer(msg.sender, baseAmount);
        
        emit LiquidityRemoved(token, msg.sender, tokenAmount, baseAmount, liquidity);
        
        return (tokenAmount, baseAmount);
    }
    
    /**
     * @dev Swap tokens
     * @param tokenIn Address of input token (token or baseToken)
     * @param tokenOut Address of output token (token or baseToken)
     * @param amountIn Amount of input tokens
     * @param minAmountOut Minimum acceptable output (slippage protection)
     */
    function swap(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 minAmountOut
    ) external nonReentrant returns (uint256 amountOut) {
        require(amountIn > 0, "Invalid amount");
        require(tokenIn != tokenOut, "Same token");
        
        address token;
        bool isBuyingToken;
        
        if (tokenIn == baseToken) {
            // Buying meme token with base token
            token = tokenOut;
            isBuyingToken = true;
        } else if (tokenOut == baseToken) {
            // Selling meme token for base token
            token = tokenIn;
            isBuyingToken = false;
        } else {
            revert("Must trade with base token");
        }
        
        Pool storage pool = pools[token];
        require(pool.exists, "Pool does not exist");
        
        // Calculate output amount with fee
        uint256 amountInWithFee = amountIn * (BASIS_POINTS - FEE_BASIS_POINTS);
        
        if (isBuyingToken) {
            // Buying token with base
            uint256 numerator = amountInWithFee * pool.token0Reserve;
            uint256 denominator = (pool.token1Reserve * BASIS_POINTS) + amountInWithFee;
            amountOut = numerator / denominator;
            
            require(amountOut >= minAmountOut, "Slippage too high");
            require(amountOut < pool.token0Reserve, "Insufficient liquidity");
            
            // Transfer tokens
            IERC20(baseToken).safeTransferFrom(msg.sender, address(this), amountIn);
            IERC20(token).safeTransfer(msg.sender, amountOut);
            
            // Update reserves
            pool.token1Reserve += amountIn;
            pool.token0Reserve -= amountOut;
        } else {
            // Selling token for base
            uint256 numerator = amountInWithFee * pool.token1Reserve;
            uint256 denominator = (pool.token0Reserve * BASIS_POINTS) + amountInWithFee;
            amountOut = numerator / denominator;
            
            require(amountOut >= minAmountOut, "Slippage too high");
            require(amountOut < pool.token1Reserve, "Insufficient liquidity");
            
            // Transfer tokens
            IERC20(token).safeTransferFrom(msg.sender, address(this), amountIn);
            IERC20(baseToken).safeTransfer(msg.sender, amountOut);
            
            // Update reserves
            pool.token0Reserve += amountIn;
            pool.token1Reserve -= amountOut;
        }
        
        uint256 fee = (amountIn * FEE_BASIS_POINTS) / BASIS_POINTS;
        
        emit Swap(msg.sender, tokenIn, tokenOut, amountIn, amountOut, fee);
        
        return amountOut;
    }
    
    /**
     * @dev Get quote for swap
     */
    function getAmountOut(
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    ) external view returns (uint256 amountOut) {
        require(amountIn > 0, "Invalid amount");
        require(tokenIn != tokenOut, "Same token");
        
        address token;
        bool isBuyingToken;
        
        if (tokenIn == baseToken) {
            token = tokenOut;
            isBuyingToken = true;
        } else if (tokenOut == baseToken) {
            token = tokenIn;
            isBuyingToken = false;
        } else {
            revert("Must trade with base token");
        }
        
        Pool storage pool = pools[token];
        require(pool.exists, "Pool does not exist");
        
        uint256 amountInWithFee = amountIn * (BASIS_POINTS - FEE_BASIS_POINTS);
        
        if (isBuyingToken) {
            uint256 numerator = amountInWithFee * pool.token0Reserve;
            uint256 denominator = (pool.token1Reserve * BASIS_POINTS) + amountInWithFee;
            amountOut = numerator / denominator;
        } else {
            uint256 numerator = amountInWithFee * pool.token1Reserve;
            uint256 denominator = (pool.token0Reserve * BASIS_POINTS) + amountInWithFee;
            amountOut = numerator / denominator;
        }
        
        return amountOut;
    }
    
    /**
     * @dev Get pool reserves
     */
    function getReserves(address token) external view returns (
        uint256 tokenReserve,
        uint256 baseReserve,
        uint256 totalLiquidity
    ) {
        Pool storage pool = pools[token];
        require(pool.exists, "Pool does not exist");
        
        return (pool.token0Reserve, pool.token1Reserve, pool.totalLiquidity);
    }
    
    /**
     * @dev Get user's liquidity in pool
     */
    function getUserLiquidity(address token, address user) external view returns (uint256) {
        return pools[token].liquidity[user];
    }
    
    /**
     * @dev Get all tokens with pools
     */
    function getAllTokens() external view returns (address[] memory) {
        return allTokens;
    }
    
    /**
     * @dev Check if pool exists
     */
    function poolExists(address token) external view returns (bool) {
        return pools[token].exists;
    }
    
    /**
     * @dev Update fee recipient (owner only)
     */
    function setFeeRecipient(address newRecipient) external onlyOwner {
        require(newRecipient != address(0), "Invalid address");
        feeRecipient = newRecipient;
    }
    
    /**
     * @dev Babylonian square root method
     */
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
