import {useState, useEffect} from "react";
import {ethers} from "ethers";
import Box from "./widgets/Box";
import Loading from "./widgets/Loading";

export default function WalletBalance({className}) {
	const [balance, setBalance] = useState(null);

	async function getBalance() {
		const [account] = await window.ethereum.request({method: "eth_requestAccounts"});
		const provider = new ethers.providers.Web3Provider(window.ethereum);
		const accountBalance = await provider.getBalance(account);
		setBalance(ethers.utils.formatEther(accountBalance)); // Q: Should this be formatted?
	}

	useEffect(() => {
		getBalance();
	}, []);

	return (
		<Box width={96} className={className}>
			{balance ? (
				<div className="p-8 space-y-2 text-gray-800 dark:text-gray-300">
					<p className="text-lg font-bold text-black dark:text-white">
						Your wallet balance: <span className="text-sm">{balance} ETH</span>
					</p>
				</div>
			) : (
				<Loading />
			)}
		</Box>
	);
}
