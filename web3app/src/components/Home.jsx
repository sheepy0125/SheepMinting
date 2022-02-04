import {useState, useEffect} from "react";
import {ethers} from "ethers";
import Box from "./widgets/Box";
import WalletBalance from "./WalletBalance";
import SheepToken from "../artifacts/contracts/SheepNFT.sol/SheepToken.json";

export default function Home() {
	// Setup the contract provider and contract objects.
	const sheepToken = "0x5FbDB2315678afecb367f032d93F642f64180aa3";
	const provider = new ethers.providers.Web3Provider(window.ethereum);
	const signer = provider.getSigner();
	const contract = new ethers.Contract(sheepToken, SheepToken.abi, signer);

	const [totalMinted, setTotalMinted] = useState(0);

	async function getCount() {
		const count = await contract.count();
		console.log({count: parseInt(count)});
		setTotalMinted(parseInt(count));
	}

	useEffect(() => {
		getCount();
	}, []);

	return (
		<>
			{/* I have spent 15 minutes attempting to center this */}
			<div className="flex items-center justify-center">
				<WalletBalance className="max-w-max" />
			</div>

			{/* NFT images */}
			<div className="grid grid-cols-1 2xl:mx-auto sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 2xl:max-w-max">
				{Array(totalMinted + 1)
					.fill(0)
					.map((_, index) => (
						<div key={index + 1}>
							<NFTImage id={index + 1} />
						</div>
					))}
			</div>
		</>
	);

	// Has access to the variables above
	function NFTImage({id}) {
		console.log({id});
		const contentID = `QmWCgENJo8oZc1PcNKeg5qjrbe5QzsFhP5DfhnCemS3JGu`;
		const metadataURI = `${contentID}/JSON_NFT_DATA-${id}.json`;
		const imageURI = `image/IMG-${id}.png`; // Local due to broken images from pinata
		console.log({metadataURI});

		const [isMinted, setIsMinted] = useState(false);

		async function getMintedStatus() {
			const response = await contract.isContentOwned(metadataURI);
			console.log({response});
			setIsMinted(response);
		}

		async function mintToken() {
			const connection = contract.connect(signer);
			const response = await contract.payToMint(connection.address, metadataURI, {value: ethers.utils.parseEther("0.05")});
			await response.wait();
			getMintedStatus();
			getCount();
		}

		async function getURI() {
			const uri = await contract.tokenURI(id);
		}

		useEffect(() => {
			getMintedStatus();
		}, []);

		return (
			<Box className={`px-8 py-2 mx-2 my-2 text-black dark:bg-slate-800 min-w-max dark:text-white ${!isMinted && "bg-white dark:bg-black"}`}>
				<p className="text-xl font-bold">Sheep NFT #{id}</p>
				<img
					src={imageURI}
					alt={isMinted ? "An already-minted sheep NFT" : "An un-minted sheep NFT! You should mint it."}
					className="w-64 mx-auto my-2 rounded-sm"
				/>
				<div className="flex">
					<p className="w-full text-lg font-bold">{!isMinted && "not"} minted</p>
					{!isMinted && (
						<p className="w-full text-right">
							<button onClick={mintToken} className="text-blue-600 underline decoration-yellow-400 dark:text-blue-200">
								Mint
							</button>
						</p>
					)}
				</div>
			</Box>
		);
	}
}
