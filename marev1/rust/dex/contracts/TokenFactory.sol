// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title MemeToken
 * @dev Standard ERC20 token created by factory
 */
contract MemeToken is ERC20, Ownable {
    uint8 private _decimals;
    
    constructor(
        string memory name,
        string memory symbol,
        uint8 decimals_,
        uint256 initialSupply,
        address creator
    ) ERC20(name, symbol) Ownable(creator) {
        _decimals = decimals_;
        _mint(creator, initialSupply);
    }
    
    function decimals() public view virtual override returns (uint8) {
        return _decimals;
    }
    
    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }
    
    function burn(uint256 amount) external {
        _burn(msg.sender, amount);
    }
}

/**
 * @title TokenFactory
 * @dev Factory contract for creating meme tokens with instant DEX listing
 */
interface IAttentionRewardsHook {
    function onTokenCreated(address creator, address token) external;
    function onTokenListed(address creator, address token, address pair) external;
}

contract TokenFactory {
    struct TokenInfo {
        address tokenAddress;
        string name;
        string symbol;
        address creator;
        uint256 createdAt;
        uint256 initialSupply;
        bool isListed;
        address listingTarget;
        address liquidityPair;
    }
    
    // Factory owner
    address public owner;
    
    // DEX contract address
    address public dexAddress;
    
    // Launch fee (in wei)
    uint256 public launchFee;
    
    // All created tokens
    address[] public allTokens;
    
    // Token info mapping
    mapping(address => TokenInfo) public tokenInfo;
    
    // Creator's tokens
    mapping(address => address[]) public creatorTokens;
    
    // Approved listing managers that can register external DEX listings
    mapping(address => bool) public listingManagers;

    // Optional on-chain activity rewards hook
    address public attentionRewardsHook;
    
    // Events
    event TokenCreated(
        address indexed tokenAddress,
        string name,
        string symbol,
        address indexed creator,
        uint256 initialSupply,
        uint256 timestamp
    );
    
    event TokenListed(
        address indexed tokenAddress,
        address indexed dexAddress,
        address indexed pairAddress,
        uint256 timestamp
    );
    
    event LaunchFeeUpdated(uint256 oldFee, uint256 newFee);
    event DexAddressUpdated(address oldDex, address newDex);
    event FeesWithdrawn(address indexed to, uint256 amount);
    event ListingManagerUpdated(address indexed account, bool allowed);
    event AttentionRewardsHookUpdated(address indexed hook);
    event AttentionRewardsHookFailed(address indexed hook, string action, address indexed tokenAddress, address indexed creator);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
    
    constructor(uint256 _launchFee) {
        owner = msg.sender;
        launchFee = _launchFee;
    }
    
    /**
     * @dev Create a new meme token
     * @param name Token name
     * @param symbol Token symbol
     * @param decimals Token decimals (usually 18)
     * @param initialSupply Initial token supply (in base units)
     */
    function createToken(
        string memory name,
        string memory symbol,
        uint8 decimals,
        uint256 initialSupply
    ) external payable returns (address) {
        require(msg.value >= launchFee, "Insufficient launch fee");
        require(bytes(name).length > 0, "Name required");
        require(bytes(symbol).length > 0, "Symbol required");
        require(initialSupply > 0, "Supply must be > 0");
        
        // Deploy new token
        MemeToken token = new MemeToken(
            name,
            symbol,
            decimals,
            initialSupply,
            msg.sender
        );
        
        address tokenAddress = address(token);
        
        // Store token info
        tokenInfo[tokenAddress] = TokenInfo({
            tokenAddress: tokenAddress,
            name: name,
            symbol: symbol,
            creator: msg.sender,
            createdAt: block.timestamp,
            initialSupply: initialSupply,
            isListed: false,
            listingTarget: address(0),
            liquidityPair: address(0)
        });
        
        // Track tokens
        allTokens.push(tokenAddress);
        creatorTokens[msg.sender].push(tokenAddress);
        
        emit TokenCreated(
            tokenAddress,
            name,
            symbol,
            msg.sender,
            initialSupply,
            block.timestamp
        );

        _notifyTokenCreated(msg.sender, tokenAddress);
        
        // Refund excess ETH
        if (msg.value > launchFee) {
            payable(msg.sender).transfer(msg.value - launchFee);
        }
        
        return tokenAddress;
    }
    
    /**
     * @dev Mark token as listed on DEX (called by creator after adding liquidity)
     */
    function markAsListed(address tokenAddress) external {
        require(tokenInfo[tokenAddress].creator == msg.sender, "Not token creator");
        require(!tokenInfo[tokenAddress].isListed, "Already listed");
        
        tokenInfo[tokenAddress].isListed = true;
        
        emit TokenListed(tokenAddress, dexAddress, address(0), block.timestamp);
        _notifyTokenListed(msg.sender, tokenAddress, address(0));
    }
    
    /**
     * @dev Register an external DEX listing through an approved listing manager.
     */
    function registerDexListing(
        address tokenAddress,
        address creator,
        address listingTarget,
        address pairAddress
    ) external {
        require(listingManagers[msg.sender], "Not listing manager");
        require(tokenInfo[tokenAddress].creator == creator, "Invalid creator");
        require(tokenInfo[tokenAddress].tokenAddress != address(0), "Unknown token");
        require(listingTarget != address(0), "Invalid listing target");
        require(pairAddress != address(0), "Invalid pair");
        require(!tokenInfo[tokenAddress].isListed, "Already listed");
        
        TokenInfo storage info = tokenInfo[tokenAddress];
        info.isListed = true;
        info.listingTarget = listingTarget;
        info.liquidityPair = pairAddress;
        
        emit TokenListed(tokenAddress, listingTarget, pairAddress, block.timestamp);
        _notifyTokenListed(creator, tokenAddress, pairAddress);
    }
    
    /**
     * @dev Get all tokens created by an address
     */
    function getCreatorTokens(address creator) external view returns (address[] memory) {
        return creatorTokens[creator];
    }
    
    /**
     * @dev Get total number of tokens created
     */
    function getTotalTokens() external view returns (uint256) {
        return allTokens.length;
    }
    
    /**
     * @dev Get token info
     */
    function getTokenInfo(address tokenAddress) external view returns (
        string memory name,
        string memory symbol,
        address creator,
        uint256 createdAt,
        uint256 initialSupply,
        bool isListed
    ) {
        TokenInfo memory info = tokenInfo[tokenAddress];
        return (
            info.name,
            info.symbol,
            info.creator,
            info.createdAt,
            info.initialSupply,
            info.isListed
        );
    }
    
    /**
     * @dev Get external listing details for a token.
     */
    function getListingInfo(address tokenAddress) external view returns (
        bool isListed,
        address listingTarget,
        address liquidityPair
    ) {
        TokenInfo memory info = tokenInfo[tokenAddress];
        return (
            info.isListed,
            info.listingTarget,
            info.liquidityPair
        );
    }
    
    /**
     * @dev Get paginated list of all tokens
     */
    function getTokens(uint256 offset, uint256 limit) external view returns (address[] memory) {
        uint256 total = allTokens.length;
        if (offset >= total) {
            return new address[](0);
        }
        
        uint256 end = offset + limit;
        if (end > total) {
            end = total;
        }
        
        uint256 size = end - offset;
        address[] memory tokens = new address[](size);
        
        for (uint256 i = 0; i < size; i++) {
            tokens[i] = allTokens[offset + i];
        }
        
        return tokens;
    }
    
    /**
     * @dev Update launch fee (owner only)
     */
    function setLaunchFee(uint256 newFee) external onlyOwner {
        uint256 oldFee = launchFee;
        launchFee = newFee;
        emit LaunchFeeUpdated(oldFee, newFee);
    }
    
    /**
     * @dev Update DEX address (owner only)
     */
    function setDexAddress(address newDex) external onlyOwner {
        require(newDex != address(0), "Invalid address");
        address oldDex = dexAddress;
        dexAddress = newDex;
        emit DexAddressUpdated(oldDex, newDex);
    }
    
    /**
     * @dev Allow a launch manager to register listings after adding liquidity.
     */
    function setListingManager(address account, bool allowed) external onlyOwner {
        require(account != address(0), "Invalid address");
        listingManagers[account] = allowed;
        emit ListingManagerUpdated(account, allowed);
    }

    /**
     * @dev Set optional on-chain attention rewards hook.
     */
    function setAttentionRewardsHook(address hook) external onlyOwner {
        attentionRewardsHook = hook;
        emit AttentionRewardsHookUpdated(hook);
    }
    
    /**
     * @dev Withdraw collected fees (owner only)
     */
    function withdrawFees() external onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "No fees to withdraw");
        
        payable(owner).transfer(balance);
        emit FeesWithdrawn(owner, balance);
    }
    
    /**
     * @dev Transfer ownership
     */
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "Invalid address");
        owner = newOwner;
    }
    
    // Allow contract to receive ETH
    receive() external payable {}

    function _notifyTokenCreated(address creator, address tokenAddress) internal {
        address hook = attentionRewardsHook;
        if (hook == address(0)) {
            return;
        }

        try IAttentionRewardsHook(hook).onTokenCreated(creator, tokenAddress) {} catch {
            emit AttentionRewardsHookFailed(hook, "created", tokenAddress, creator);
        }
    }

    function _notifyTokenListed(address creator, address tokenAddress, address pairAddress) internal {
        address hook = attentionRewardsHook;
        if (hook == address(0)) {
            return;
        }

        try IAttentionRewardsHook(hook).onTokenListed(creator, tokenAddress, pairAddress) {} catch {
            emit AttentionRewardsHookFailed(hook, "listed", tokenAddress, creator);
        }
    }
}
