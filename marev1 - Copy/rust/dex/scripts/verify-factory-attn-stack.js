const hre = require("hardhat");

const FACTORY_ADDRESS = process.env.FACTORY_ADDRESS;
const LISTING_MANAGER = process.env.LISTING_MANAGER;
const ATTN_HOOK = process.env.ATTN_REWARDS_HOOK || "0x88cb287A480DCE4b88e6A0263dc4BCfc4cf7E7d6";

async function main() {
  if (!FACTORY_ADDRESS) throw new Error("FACTORY_ADDRESS is required");
  if (!LISTING_MANAGER) throw new Error("LISTING_MANAGER is required");

  const factory = await hre.ethers.getContractAt("TokenFactory", FACTORY_ADDRESS);
  const rewards = await hre.ethers.getContractAt("AttentionActivityRewards", ATTN_HOOK);

  const [dexAddress, rewardHook, authorized] = await Promise.all([
    factory.dexAddress(),
    factory.attentionRewardsHook(),
    rewards.authorizedHooks(FACTORY_ADDRESS),
  ]);

  const isManager = await factory.listingManagers(LISTING_MANAGER);

  console.log(JSON.stringify({
    factory: FACTORY_ADDRESS,
    dexAddress,
    listingManager: LISTING_MANAGER,
    listingManagerAuthorized: isManager,
    attentionRewardsHook: rewardHook,
    rewardsHookAuthorizesFactory: authorized,
  }, null, 2));
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
