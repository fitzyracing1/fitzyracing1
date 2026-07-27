const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Meme Coin Factory", function () {
  let factory, dex, baseToken;
  let owner, user1, user2;
  const LAUNCH_FEE = ethers.parseEther("0.001");
  
  beforeEach(async function () {
    [owner, user1, user2] = await ethers.getSigners();
    
    // Deploy mock USDC
    const ERC20Mock = await ethers.getContractFactory("ERC20Mock");
    baseToken = await ERC20Mock.deploy("USD Coin", "USDC", 6);
    await baseToken.waitForDeployment();
    
    // Mint USDC to users
    await baseToken.mint(user1.address, ethers.parseUnits("10000", 6));
    await baseToken.mint(user2.address, ethers.parseUnits("10000", 6));
    
    // Deploy Factory
    const TokenFactory = await ethers.getContractFactory("TokenFactory");
    factory = await TokenFactory.deploy(LAUNCH_FEE);
    await factory.waitForDeployment();
    
    // Deploy DEX
    const MemeDex = await ethers.getContractFactory("MemeDex");
    dex = await MemeDex.deploy(await baseToken.getAddress(), owner.address);
    await dex.waitForDeployment();
    
    // Link factory to DEX
    await factory.setDexAddress(await dex.getAddress());
  });
  
  describe("Token Creation", function () {
    it("Should create a new token with correct fee", async function () {
      const tx = await factory.connect(user1).createToken(
        "Pepe Coin",
        "PEPE",
        18,
        ethers.parseEther("1000000"),
        { value: LAUNCH_FEE }
      );
      
      const receipt = await tx.wait();
      const event = receipt.logs.find(log => {
        try {
          return factory.interface.parseLog(log).name === "TokenCreated";
        } catch {
          return false;
        }
      });
      
      expect(event).to.not.be.undefined;
      
      const tokenAddress = await factory.allTokens(0);
      expect(tokenAddress).to.not.equal(ethers.ZeroAddress);
      
      // Check token info
      const [name, symbol, creator, , initialSupply] = await factory.getTokenInfo(tokenAddress);
      expect(name).to.equal("Pepe Coin");
      expect(symbol).to.equal("PEPE");
      expect(creator).to.equal(user1.address);
      expect(initialSupply).to.equal(ethers.parseEther("1000000"));
    });
    
    it("Should fail without sufficient fee", async function () {
      await expect(
        factory.connect(user1).createToken(
          "Pepe Coin",
          "PEPE",
          18,
          ethers.parseEther("1000000"),
          { value: ethers.parseEther("0.0001") }
        )
      ).to.be.revertedWith("Insufficient launch fee");
    });
    
    it("Should refund excess ETH", async function () {
      const balanceBefore = await ethers.provider.getBalance(user1.address);
      
      const tx = await factory.connect(user1).createToken(
        "Pepe Coin",
        "PEPE",
        18,
        ethers.parseEther("1000000"),
        { value: ethers.parseEther("0.01") }
      );
      
      const receipt = await tx.wait();
      const gasUsed = receipt.gasUsed * receipt.gasPrice;
      const balanceAfter = await ethers.provider.getBalance(user1.address);
      
      const expectedBalance = balanceBefore - LAUNCH_FEE - gasUsed;
      expect(balanceAfter).to.be.closeTo(expectedBalance, ethers.parseEther("0.0001"));
    });
    
    it("Should track creator's tokens", async function () {
      await factory.connect(user1).createToken(
        "Pepe Coin",
        "PEPE",
        18,
        ethers.parseEther("1000000"),
        { value: LAUNCH_FEE }
      );
      
      await factory.connect(user1).createToken(
        "Doge Coin",
        "DOGE",
        18,
        ethers.parseEther("500000"),
        { value: LAUNCH_FEE }
      );
      
      const tokens = await factory.getCreatorTokens(user1.address);
      expect(tokens.length).to.equal(2);
    });
  });
  
  describe("Pool Creation", function () {
    let tokenAddress;
    
    beforeEach(async function () {
      const tx = await factory.connect(user1).createToken(
        "Pepe Coin",
        "PEPE",
        18,
        ethers.parseEther("1000000"),
        { value: LAUNCH_FEE }
      );
      await tx.wait();
      
      tokenAddress = await factory.allTokens(0);
    });
    
    it("Should create liquidity pool", async function () {
      const MemeToken = await ethers.getContractFactory("MemeToken");
      const token = MemeToken.attach(tokenAddress);
      
      const tokenAmount = ethers.parseEther("100000");
      const baseAmount = ethers.parseUnits("1000", 6);
      
      // Approve tokens
      await token.connect(user1).approve(await dex.getAddress(), tokenAmount);
      await baseToken.connect(user1).approve(await dex.getAddress(), baseAmount);
      
      // Create pool
      await dex.connect(user1).createPool(tokenAddress, tokenAmount, baseAmount);
      
      const [tokenReserve, baseReserve] = await dex.getReserves(tokenAddress);
      expect(tokenReserve).to.equal(tokenAmount);
      expect(baseReserve).to.equal(baseAmount);
    });
    
    it("Should not create duplicate pool", async function () {
      const MemeToken = await ethers.getContractFactory("MemeToken");
      const token = MemeToken.attach(tokenAddress);
      
      const tokenAmount = ethers.parseEther("100000");
      const baseAmount = ethers.parseUnits("1000", 6);
      
      await token.connect(user1).approve(await dex.getAddress(), tokenAmount * 2n);
      await baseToken.connect(user1).approve(await dex.getAddress(), baseAmount * 2n);
      
      await dex.connect(user1).createPool(tokenAddress, tokenAmount, baseAmount);
      
      await expect(
        dex.connect(user1).createPool(tokenAddress, tokenAmount, baseAmount)
      ).to.be.revertedWith("Pool already exists");
    });
  });
  
  describe("Swapping", function () {
    let tokenAddress;
    
    beforeEach(async function () {
      // Create token
      const tx = await factory.connect(user1).createToken(
        "Pepe Coin",
        "PEPE",
        18,
        ethers.parseEther("1000000"),
        { value: LAUNCH_FEE }
      );
      await tx.wait();
      
      tokenAddress = await factory.allTokens(0);
      
      // Create pool
      const MemeToken = await ethers.getContractFactory("MemeToken");
      const token = MemeToken.attach(tokenAddress);
      
      const tokenAmount = ethers.parseEther("100000");
      const baseAmount = ethers.parseUnits("1000", 6);
      
      await token.connect(user1).approve(await dex.getAddress(), tokenAmount);
      await baseToken.connect(user1).approve(await dex.getAddress(), baseAmount);
      await dex.connect(user1).createPool(tokenAddress, tokenAmount, baseAmount);
    });
    
    it("Should swap base token for meme token", async function () {
      const swapAmount = ethers.parseUnits("10", 6); // 10 USDC
      
      await baseToken.connect(user2).approve(await dex.getAddress(), swapAmount);
      
      const amountOut = await dex.getAmountOut(
        await baseToken.getAddress(),
        tokenAddress,
        swapAmount
      );
      
      await dex.connect(user2).swap(
        await baseToken.getAddress(),
        tokenAddress,
        swapAmount,
        0
      );
      
      const MemeToken = await ethers.getContractFactory("MemeToken");
      const token = MemeToken.attach(tokenAddress);
      const balance = await token.balanceOf(user2.address);
      
      expect(balance).to.be.closeTo(amountOut, ethers.parseEther("0.01"));
    });
    
    it("Should swap meme token for base token", async function () {
      // First buy some tokens
      const buyAmount = ethers.parseUnits("10", 6);
      await baseToken.connect(user2).approve(await dex.getAddress(), buyAmount);
      await dex.connect(user2).swap(
        await baseToken.getAddress(),
        tokenAddress,
        buyAmount,
        0
      );
      
      const MemeToken = await ethers.getContractFactory("MemeToken");
      const token = MemeToken.attach(tokenAddress);
      const tokenBalance = await token.balanceOf(user2.address);
      
      // Then sell them
      await token.connect(user2).approve(await dex.getAddress(), tokenBalance);
      await dex.connect(user2).swap(
        tokenAddress,
        await baseToken.getAddress(),
        tokenBalance,
        0
      );
      
      const baseBalance = await baseToken.balanceOf(user2.address);
      expect(baseBalance).to.be.lt(ethers.parseUnits("10000", 6)); // Started with 10000
      expect(baseBalance).to.be.gt(ethers.parseUnits("9990", 6)); // Lost to fees
    });
    
    it("Should fail with insufficient slippage protection", async function () {
      const swapAmount = ethers.parseUnits("10", 6);
      await baseToken.connect(user2).approve(await dex.getAddress(), swapAmount);
      
      const amountOut = await dex.getAmountOut(
        await baseToken.getAddress(),
        tokenAddress,
        swapAmount
      );
      
      await expect(
        dex.connect(user2).swap(
          await baseToken.getAddress(),
          tokenAddress,
          swapAmount,
          amountOut * 2n // Expect double
        )
      ).to.be.revertedWith("Slippage too high");
    });

    it("Should launch and trade Joshua end to end", async function () {
      const launchTx = await factory.connect(user1).createToken(
        "Joshua",
        "JOSH",
        18,
        ethers.parseEther("1000000"),
        { value: LAUNCH_FEE }
      );
      await launchTx.wait();

      const joshuaAddress = await factory.allTokens(1);
      const MemeToken = await ethers.getContractFactory("MemeToken");
      const joshua = MemeToken.attach(joshuaAddress);

      const tokenAmount = ethers.parseEther("150000");
      const baseAmount = ethers.parseUnits("1500", 6);

      await joshua.connect(user1).approve(await dex.getAddress(), tokenAmount);
      await baseToken.connect(user1).approve(await dex.getAddress(), baseAmount);
      await dex.connect(user1).createPool(joshuaAddress, tokenAmount, baseAmount);

      const buyAmount = ethers.parseUnits("25", 6);
      await baseToken.connect(user2).approve(await dex.getAddress(), buyAmount);

      const quoteOut = await dex.getAmountOut(
        await baseToken.getAddress(),
        joshuaAddress,
        buyAmount
      );

      await expect(
        dex.connect(user2).swap(
          await baseToken.getAddress(),
          joshuaAddress,
          buyAmount,
          0
        )
      ).to.emit(dex, "Swap");

      const joshBalance = await joshua.balanceOf(user2.address);
      expect(joshBalance).to.equal(quoteOut);

      await joshua.connect(user2).approve(await dex.getAddress(), joshBalance);
      await expect(
        dex.connect(user2).swap(
          joshuaAddress,
          await baseToken.getAddress(),
          joshBalance,
          0
        )
      ).to.emit(dex, "Swap");

      const endingBaseBalance = await baseToken.balanceOf(user2.address);
      expect(endingBaseBalance).to.be.lt(ethers.parseUnits("10000", 6));
      expect(endingBaseBalance).to.be.gt(ethers.parseUnits("9990", 6));
    });
  });
  
  describe("Admin Functions", function () {
    it("Should allow owner to update launch fee", async function () {
      const newFee = ethers.parseEther("0.002");
      await factory.setLaunchFee(newFee);
      expect(await factory.launchFee()).to.equal(newFee);
    });
    
    it("Should not allow non-owner to update launch fee", async function () {
      await expect(
        factory.connect(user1).setLaunchFee(ethers.parseEther("0.002"))
      ).to.be.revertedWith("Not owner");
    });
    
    it("Should allow owner to withdraw fees", async function () {
      await factory.connect(user1).createToken(
        "Pepe Coin",
        "PEPE",
        18,
        ethers.parseEther("1000000"),
        { value: LAUNCH_FEE }
      );
      
      const balanceBefore = await ethers.provider.getBalance(owner.address);
      const tx = await factory.withdrawFees();
      const receipt = await tx.wait();
      const gasUsed = receipt.gasUsed * receipt.gasPrice;
      const balanceAfter = await ethers.provider.getBalance(owner.address);
      
      expect(balanceAfter).to.be.closeTo(
        balanceBefore + LAUNCH_FEE - gasUsed,
        ethers.parseEther("0.0001")
      );
    });
  });
});
