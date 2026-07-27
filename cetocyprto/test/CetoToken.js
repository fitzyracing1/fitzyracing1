const { expect } = require("chai");
const { ethers, network } = require("hardhat");

describe("CetoToken", function () {
  const decimals = 18;
  const initialSupply = ethers.parseUnits("1000000", decimals);

  async function deployToken() {
    const [owner, user] = await ethers.getSigners();
    const Token = await ethers.getContractFactory("CetoToken");
    const token = await Token.deploy(initialSupply, owner.address);
    return { token, owner, user };
  }

  it("deploys with correct metadata and initial supply", async function () {
    const { token, owner } = await deployToken();
    expect(await token.name()).to.equal("Ceto");
    expect(await token.symbol()).to.equal("CETO");
    expect(await token.totalSupply()).to.equal(initialSupply);
    expect(await token.balanceOf(owner.address)).to.equal(initialSupply);
  });

  it("enforces 20% rolling mint capacity", async function () {
    const { token, owner, user } = await deployToken();
    const limit = await token.rollingLimit();
    const mintAmount = limit - 1n;

    await token.connect(owner).mint(user.address, mintAmount);
    expect(await token.balanceOf(user.address)).to.equal(mintAmount);

    await expect(
      token.connect(owner).mint(user.address, 2n)
    ).to.be.revertedWith("Rolling capacity exceeded");
  });

  it("resets capacity after the rolling window", async function () {
    const { token, owner, user } = await deployToken();
    const limit = await token.rollingLimit();

    await token.connect(owner).mint(user.address, limit);
    expect(await token.remainingCapacity()).to.equal(0);

    await network.provider.send("evm_increaseTime", [24 * 60 * 60]);
    await network.provider.send("evm_mine");

    const newLimit = await token.rollingLimit();
    expect(await token.remainingCapacity()).to.equal(newLimit);

    await token.connect(owner).mint(user.address, newLimit);
    expect(await token.balanceOf(user.address)).to.equal(newLimit + limit);
  });
});
