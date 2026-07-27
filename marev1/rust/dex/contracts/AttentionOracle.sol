// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

contract AttentionOracle is Ownable {
    struct DayData {
        bytes32 merkleRoot;
        uint256 totalScore;
        uint256 emissionAmount;
        bool finalized;
    }

    mapping(uint256 => DayData) public dayData;

    event DaySubmitted(uint256 indexed day, bytes32 merkleRoot, uint256 totalScore, uint256 emissionAmount);
    event DayFinalized(uint256 indexed day);

    constructor(address initialOwner) Ownable(initialOwner) {}

    function submitDayRoot(
        uint256 day,
        bytes32 merkleRoot,
        uint256 totalScore,
        uint256 emissionAmount
    ) external onlyOwner {
        require(merkleRoot != bytes32(0), "Invalid root");
        require(dayData[day].merkleRoot == bytes32(0), "Day already submitted");
        require(totalScore > 0, "Invalid total score");
        require(emissionAmount > 0, "Invalid emission");

        dayData[day] = DayData({
            merkleRoot: merkleRoot,
            totalScore: totalScore,
            emissionAmount: emissionAmount,
            finalized: false
        });

        emit DaySubmitted(day, merkleRoot, totalScore, emissionAmount);
    }

    function finalizeDay(uint256 day) external onlyOwner {
        DayData storage data = dayData[day];
        require(data.merkleRoot != bytes32(0), "Day not submitted");
        require(!data.finalized, "Day already finalized");

        data.finalized = true;
        emit DayFinalized(day);
    }

    function getDayData(uint256 day) external view returns (bytes32, uint256, uint256, bool) {
        DayData memory data = dayData[day];
        return (data.merkleRoot, data.totalScore, data.emissionAmount, data.finalized);
    }
}
