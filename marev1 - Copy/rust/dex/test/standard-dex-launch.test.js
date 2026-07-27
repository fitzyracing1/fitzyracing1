const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Standard DEX launch flow", function () {
  let baseToken;
  let tokenFactory;
  let listingManager;
  let dexFactory;
  let dexRouter;
  let owner;
  let creator;

  const LAUNCH_FEE = ethers.parseEther("0.001");

  beforeEach(async function () {
    [owner, creator] = await ethers.getSigners();

    const ERC20Mock = await ethers.getContractFactory("ERC20Mock");
    baseToken = await ERC20Mock.deploy("USD Coin", "USDC", 6);
    await baseToken.waitForDeployment();
    await baseToken.mint(creator.address, ethers.parseUnits("10000", 6));

    const TokenFactory = await ethers.getContractFactory("TokenFactory");
    tokenFactory = await TokenFactory.deploy(LAUNCH_FEE);
    await tokenFactory.waitForDeployment();

    const FactoryMock = await ethers.getContractFactory("UniswapV2FactoryMock");
    dexFactory = await FactoryMock.deploy();
    await dexFactory.waitForDeployment();

    const RouterMock = await ethers.getContractFactory("UniswapV2RouterMock");
    dexRouter = await RouterMock.deploy(await dexFactory.getAddress());
    await dexRouter.waitForDeployment();

    await tokenFactory.setDexAddress(await dexRouter.getAddress());

    const StandardDexLiquidityManager = await ethers.getContractFactory("StandardDexLiquidityManager");
    listingManager = await StandardDexLiquidityManager.deploy(
      await baseToken.getAddress(),
      await dexRouter.getAddress(),
      await dexFactory.getAddress(),
      await tokenFactory.getAddress()
    );
    await listingManager.waitForDeployment();

    await tokenFactory.setListingManager(await listingManager.getAddress(), true);
  });

  it("creates a standard pair, adds liquidity, and records the listing", async function () {
    await tokenFactory.connect(creator).createToken(
      "Pepe Coin",
      "PEPE",
      18,
      ethers.parseEther("1000000"),
      { value: LAUNCH_FEE }
    );

    const tokenAddress = await tokenFactory.allTokens(0);
    const MemeToken = await ethers.getContractFactory("MemeToken");
    const token = MemeToken.attach(tokenAddress);

    const tokenAmount = ethers.parseEther("100000");
    const baseAmount = ethers.parseUnits("1000", 6);

    await token.connect(creator).approve(await listingManager.getAddress(), tokenAmount);
    await baseToken.connect(creator).approve(await listingManager.getAddress(), baseAmount);

    await listingManager.connect(creator).launchToken(
      tokenAddress,
      tokenAmount,
      baseAmount,
      tokenAmount * 95n / 100n,
      baseAmount * 95n / 100n,
      (await ethers.provider.getBlock("latest")).timestamp + 1200
    );

    const pairAddress = await dexFactory.getPair(tokenAddress, await baseToken.getAddress());
    expect(pairAddress).to.not.equal(ethers.ZeroAddress);

    const [isListed, listingTarget, liquidityPair] = await tokenFactory.getListingInfo(tokenAddress);
    expect(isListed).to.equal(true);
    expect(listingTarget).to.equal(await dexRouter.getAddress());
    expect(liquidityPair).to.equal(pairAddress);

    expect(await token.balanceOf(pairAddress)).to.equal(tokenAmount);
    expect(await baseToken.balanceOf(pairAddress)).to.equal(baseAmount);
  });
});
