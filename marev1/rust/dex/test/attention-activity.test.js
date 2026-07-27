const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Attention Activity Rewards", function () {
  let owner, creator, other;
  let token, rewards, factory;

  const LAUNCH_FEE = ethers.parseEther("0.001");
  const createdAmount = ethers.parseEther("10");
  const listedAmount = ethers.parseEther("25");

  beforeEach(async function () {
    [owner, creator, other] = await ethers.getSigners();

    const AttentionToken = await ethers.getContractFactory("AttentionToken");
    token = await AttentionToken.deploy(
      "Attention Token",
      "ATTN",
      ethers.parseEther("1000000000"),
      owner.address
    );
    await token.waitForDeployment();

    const AttentionActivityRewards = await ethers.getContractFactory("AttentionActivityRewards");
    rewards = await AttentionActivityRewards.deploy(
      await token.getAddress(),
      0,
      86400,
      100,
      createdAmount,
      400,
      listedAmount,
      owner.address
    );
    await rewards.waitForDeployment();

    await token.setMinter(await rewards.getAddress(), true);

    const TokenFactory = await ethers.getContractFactory("TokenFactory");
    factory = await TokenFactory.deploy(LAUNCH_FEE);
    await factory.waitForDeployment();

    await factory.setAttentionRewardsHook(await rewards.getAddress());
    await rewards.setAuthorizedHook(await factory.getAddress(), true);
  });

  it("accrues on-chain rewards when a token is created", async function () {
    await factory.connect(creator).createToken(
      "Joshua",
      "JOSH",
      18,
      ethers.parseEther("1000000"),
      { value: LAUNCH_FEE }
    );

    const day = await rewards.currentDay();
    const preview = await rewards.previewRewards(day, creator.address);
    expect(preview[0]).to.equal(100);
    expect(preview[1]).to.equal(createdAmount);
    expect(preview[2]).to.equal(false);
  });

  it("accrues listing rewards and allows direct claim", async function () {
    await factory.connect(creator).createToken(
      "Joshua",
      "JOSH",
      18,
      ethers.parseEther("1000000"),
      { value: LAUNCH_FEE }
    );

    const tokenAddress = await factory.allTokens(0);
    await factory.setListingManager(owner.address, true);
    await factory.registerDexListing(tokenAddress, creator.address, other.address, owner.address);

    const day = await rewards.currentDay();
    const preview = await rewards.previewRewards(day, creator.address);
    expect(preview[0]).to.equal(500);
    expect(preview[1]).to.equal(createdAmount + listedAmount);

    await expect(rewards.connect(creator).claim(day))
      .to.emit(rewards, "Claimed")
      .withArgs(day, creator.address, 500, createdAmount + listedAmount);

    expect(await token.balanceOf(creator.address)).to.equal(createdAmount + listedAmount);
  });
});
