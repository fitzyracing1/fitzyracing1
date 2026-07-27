const { expect } = require("chai");
const { ethers } = require("hardhat");

function leafHash(day, wallet, score, amount) {
  const coder = ethers.AbiCoder.defaultAbiCoder();
  return ethers.keccak256(
    coder.encode(["uint256", "address", "uint256", "uint256"], [day, wallet, score, amount])
  );
}

function hashPair(a, b) {
  return a.toLowerCase() < b.toLowerCase()
    ? ethers.keccak256(ethers.concat([a, b]))
    : ethers.keccak256(ethers.concat([b, a]));
}

describe("Attention V1", function () {
  let owner, alice, bob;
  let token, oracle, distributor;

  const day = 1;
  const aliceScore = 250n;
  const bobScore = 750n;
  const aliceReward = ethers.parseEther("100");
  const bobReward = ethers.parseEther("300");

  let aliceLeaf;
  let bobLeaf;
  let merkleRoot;
  let totalScore;
  let totalEmission;

  beforeEach(async function () {
    [owner, alice, bob] = await ethers.getSigners();

    const AttentionToken = await ethers.getContractFactory("AttentionToken");
    token = await AttentionToken.deploy(
      "Attention Token",
      "ATTN",
      ethers.parseEther("1000000000"),
      owner.address
    );
    await token.waitForDeployment();

    const AttentionOracle = await ethers.getContractFactory("AttentionOracle");
    oracle = await AttentionOracle.deploy(owner.address);
    await oracle.waitForDeployment();

    const AttentionDistributor = await ethers.getContractFactory("AttentionDistributor");
    distributor = await AttentionDistributor.deploy(
      await token.getAddress(),
      await oracle.getAddress(),
      owner.address
    );
    await distributor.waitForDeployment();

    await token.setMinter(await distributor.getAddress(), true);

    aliceLeaf = leafHash(day, alice.address, aliceScore, aliceReward);
    bobLeaf = leafHash(day, bob.address, bobScore, bobReward);
    merkleRoot = hashPair(aliceLeaf, bobLeaf);
    totalScore = aliceScore + bobScore;
    totalEmission = aliceReward + bobReward;
  });

  it("claims successfully with a valid proof", async function () {
    await oracle.submitDayRoot(day, merkleRoot, totalScore, totalEmission);
    await oracle.finalizeDay(day);

    await expect(distributor.connect(alice).claim(day, aliceScore, aliceReward, [bobLeaf]))
      .to.emit(distributor, "Claimed")
      .withArgs(day, alice.address, aliceScore, aliceReward);

    expect(await token.balanceOf(alice.address)).to.equal(aliceReward);
    expect(await distributor.claimed(day, alice.address)).to.equal(true);
  });

  it("rejects duplicate claim", async function () {
    await oracle.submitDayRoot(day, merkleRoot, totalScore, totalEmission);
    await oracle.finalizeDay(day);

    await distributor.connect(alice).claim(day, aliceScore, aliceReward, [bobLeaf]);

    await expect(
      distributor.connect(alice).claim(day, aliceScore, aliceReward, [bobLeaf])
    ).to.be.revertedWith("Already claimed");
  });

  it("rejects claim before day is finalized", async function () {
    await oracle.submitDayRoot(day, merkleRoot, totalScore, totalEmission);

    await expect(
      distributor.connect(alice).claim(day, aliceScore, aliceReward, [bobLeaf])
    ).to.be.revertedWith("Day not finalized");
  });

  it("rejects invalid proof", async function () {
    await oracle.submitDayRoot(day, merkleRoot, totalScore, totalEmission);
    await oracle.finalizeDay(day);

    await expect(
      distributor.connect(alice).claim(day, aliceScore, aliceReward + 1n, [bobLeaf])
    ).to.be.revertedWith("Invalid proof");
  });

  it("owner can rotate oracle and token addresses", async function () {
    const AttentionOracle = await ethers.getContractFactory("AttentionOracle");
    const newOracle = await AttentionOracle.deploy(owner.address);
    await newOracle.waitForDeployment();

    const AttentionToken = await ethers.getContractFactory("AttentionToken");
    const newToken = await AttentionToken.deploy(
      "New Attention",
      "NATN",
      ethers.parseEther("1000000000"),
      owner.address
    );
    await newToken.waitForDeployment();

    await distributor.setOracle(await newOracle.getAddress());
    await distributor.setToken(await newToken.getAddress());

    expect(await distributor.attentionOracle()).to.equal(await newOracle.getAddress());
    expect(await distributor.attentionToken()).to.equal(await newToken.getAddress());
  });
});
