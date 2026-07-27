// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";

interface IAttentionToken {
    function mint(address to, uint256 amount) external;
}

interface IAttentionOracle {
    function getDayData(uint256 day) external view returns (bytes32, uint256, uint256, bool);
}

contract AttentionDistributor is Ownable, ReentrancyGuard {
    IAttentionToken public attentionToken;
    IAttentionOracle public attentionOracle;

    mapping(uint256 => mapping(address => bool)) public claimed;

    event Claimed(uint256 indexed day, address indexed account, uint256 score, uint256 amount);
    event OracleUpdated(address indexed oldOracle, address indexed newOracle);
    event TokenUpdated(address indexed oldToken, address indexed newToken);

    constructor(address token_, address oracle_, address initialOwner) Ownable(initialOwner) {
        require(token_ != address(0), "Invalid token");
        require(oracle_ != address(0), "Invalid oracle");

        attentionToken = IAttentionToken(token_);
        attentionOracle = IAttentionOracle(oracle_);
    }

    function setOracle(address newOracle) external onlyOwner {
        require(newOracle != address(0), "Invalid oracle");
        address oldOracle = address(attentionOracle);
        attentionOracle = IAttentionOracle(newOracle);
        emit OracleUpdated(oldOracle, newOracle);
    }

    function setToken(address newToken) external onlyOwner {
        require(newToken != address(0), "Invalid token");
        address oldToken = address(attentionToken);
        attentionToken = IAttentionToken(newToken);
        emit TokenUpdated(oldToken, newToken);
    }

    function claim(
        uint256 day,
        uint256 score,
        uint256 amount,
        bytes32[] calldata proof
    ) external nonReentrant {
        require(!claimed[day][msg.sender], "Already claimed");

        (bytes32 root, , , bool finalized) = attentionOracle.getDayData(day);
        require(root != bytes32(0), "Day not submitted");
        require(finalized, "Day not finalized");

        bytes32 leaf = keccak256(abi.encode(day, msg.sender, score, amount));
        require(MerkleProof.verifyCalldata(proof, root, leaf), "Invalid proof");

        claimed[day][msg.sender] = true;
        attentionToken.mint(msg.sender, amount);

        emit Claimed(day, msg.sender, score, amount);
    }
}
