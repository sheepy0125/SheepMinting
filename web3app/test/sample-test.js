const {expect} = require("chai");
const {ethers} = require("hardhat");

describe("SheepToken", function () {
	it("Should mint and transfer an NFT to someone", async function () {
		const SheepToken = await ethers.getContractFactory("SheepToken");
		const sheepToken = await SheepToken.deploy();
		await sheepToken.deployed();

		const recipient = "0x9965507d1a55bcc2695c58ba16fb37d819b0a4dc";
		const metadataURI = "cid/test.png";

		let balance = await sheepToken.balanceOf(recipient);
		expect(balance).to.equal(0);

		const newMintedToken = await sheepToken.payToMint(recipient, metadataURI, {
			value: ethers.utils.parseEther("0.05"),
		});

		await newMintedToken.wait();

		balance = await sheepToken.balanceOf(recipient);
		expect(balance).to.equal(1);

		expect(await sheepToken.isContentOwned(metadataURI)).to.equal(true);
	});
});
