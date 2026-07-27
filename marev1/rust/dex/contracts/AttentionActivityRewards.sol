// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

interface IAttentionMintableToken {
    function mint(address to, uint256 amount) external;
}

contract AttentionActivityRewards is Ownable, ReentrancyGuard {
    struct RewardConfig {
        uint256 score;
        uint256 amount;
    }

    IAttentionMintableToken public attentionToken;
    uint256 public immutable startTimestamp;
    uint256 public immutable dayDuration;

    RewardConfig public tokenCreatedReward;
    RewardConfig public tokenListedReward;

    mapping(address => bool) public authorizedHooks;
    mapping(uint256 => mapping(address => uint256)) public pendingScores;
    mapping(uint256 => mapping(address => uint256)) public pendingAmounts;
    mapping(uint256 => mapping(address => bool)) public claimed;

    event AuthorizedHookUpdated(address indexed hook, bool allowed);
    event RewardConfigUpdated(uint256 createdScore, uint256 createdAmount, uint256 listedScore, uint256 listedAmount);
    event RewardAccrued(
        uint256 indexed day,
        address indexed account,
        address indexed token,
        string action,
        uint256 score,
        uint256 amount
    );
    event Claimed(uint256 indexed day, address indexed account, uint256 score, uint256 amount);
    event TokenUpdated(address indexed oldToken, address indexed newToken);

    modifier onlyAuthorizedHook() {
        require(authorizedHooks[msg.sender], "Not authorized hook");
        _;
    }

    constructor(
        address token_,
        uint256 startTimestamp_,
        uint256 dayDuration_,
        uint256 createdScore_,
        uint256 createdAmount_,
        uint256 listedScore_,
        uint256 listedAmount_,
        address initialOwner
    ) Ownable(initialOwner) {
        require(token_ != address(0), "Invalid token");
        require(dayDuration_ > 0, "Invalid duration");

        attentionToken = IAttentionMintableToken(token_);
        startTimestamp = startTimestamp_;
        dayDuration = dayDuration_;
        tokenCreatedReward = RewardConfig({ score: createdScore_, amount: createdAmount_ });
        tokenListedReward = RewardConfig({ score: listedScore_, amount: listedAmount_ });
    }

    function currentDay() public view returns (uint256) {
        if (block.timestamp < startTimestamp) {
            return 0;
        }
        return ((block.timestamp - startTimestamp) / dayDuration) + 1;
    }

    function setAuthorizedHook(address hook, bool allowed) external onlyOwner {
        require(hook != address(0), "Invalid hook");
        authorizedHooks[hook] = allowed;
        emit AuthorizedHookUpdated(hook, allowed);
    }

    function setToken(address newToken) external onlyOwner {
        require(newToken != address(0), "Invalid token");
        address oldToken = address(attentionToken);
        attentionToken = IAttentionMintableToken(newToken);
        emit TokenUpdated(oldToken, newToken);
    }

    function setRewardConfig(
        uint256 createdScore_,
        uint256 createdAmount_,
        uint256 listedScore_,
        uint256 listedAmount_
    ) external onlyOwner {
        tokenCreatedReward = RewardConfig({ score: createdScore_, amount: createdAmount_ });
        tokenListedReward = RewardConfig({ score: listedScore_, amount: listedAmount_ });
        emit RewardConfigUpdated(createdScore_, createdAmount_, listedScore_, listedAmount_);
    }

    function onTokenCreated(address creator, address token) external onlyAuthorizedHook {
        _accrue(currentDay(), creator, token, "created", tokenCreatedReward.score, tokenCreatedReward.amount);
    }

    function onTokenListed(address creator, address token, address) external onlyAuthorizedHook {
        _accrue(currentDay(), creator, token, "listed", tokenListedReward.score, tokenListedReward.amount);
    }

    function claim(uint256 day) external nonReentrant {
        require(!claimed[day][msg.sender], "Already claimed");

        uint256 amount = pendingAmounts[day][msg.sender];
        uint256 score = pendingScores[day][msg.sender];
        require(amount > 0, "No rewards");

        claimed[day][msg.sender] = true;
        pendingAmounts[day][msg.sender] = 0;
        pendingScores[day][msg.sender] = 0;

        attentionToken.mint(msg.sender, amount);
        emit Claimed(day, msg.sender, score, amount);
    }

    function previewRewards(uint256 day, address account) external view returns (uint256 score, uint256 amount, bool alreadyClaimed) {
        return (pendingScores[day][account], pendingAmounts[day][account], claimed[day][account]);
    }

    function _accrue(
        uint256 day,
        address creator,
        address token,
        string memory action,
        uint256 score,
        uint256 amount
    ) internal {
        require(creator != address(0), "Invalid creator");
        if (score == 0 && amount == 0) {
            return;
        }

        pendingScores[day][creator] += score;
        pendingAmounts[day][creator] += amount;

        emit RewardAccrued(day, creator, token, action, score, amount);
    }
}
