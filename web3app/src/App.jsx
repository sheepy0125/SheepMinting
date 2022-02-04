import {useState, useEffect} from "react";
import Install from "./components/Installation";
import Home from "./components/Home";
import Loading from "./components/widgets/Loading";

export default function App() {
	// MetaMask installation check can take a bit of time
	const [loading, setLoading] = useState(true);
	setTimeout(() => setLoading(false), 100);

	// MetaMask installation checks
	const [hasMetaMask, setHasMetaMask] = useState(false);

	function checkMetaMaskInstalled() {
		setHasMetaMask(!!window.ethereum);
	}
	useEffect(checkMetaMaskInstalled, []);

	// Dark theme
	const [theme, setTheme] = useState(localStorage.theme || "light");
	useEffect(() => {
		if (localStorage.theme === "dark" || (!("theme" in localStorage) && window.matchMedia("(prefers-color-scheme: dark)").matches)) {
			document.documentElement.classList.add("dark");
		} else {
			document.documentElement.classList.remove("dark");
		}
	}, [theme]);

	function toggleColorScheme() {
		localStorage.theme = localStorage.theme === "dark" ? "light" : "dark";
		setTheme(localStorage.theme);
	}

	return (
		<main>
			{loading ? <Loading /> : <>{!hasMetaMask ? <Install onInstall={checkMetaMaskInstalled} /> : <Home />}</>}
			<button
				onClick={toggleColorScheme}
				className={`
							block p-2 mx-auto my-2 bg-indigo-400 rounded-md w-max md:absolute hover:bg-indigo-300 drop-shadow-xl
							md:right-2 md:top-2 text-slate-900 dark:bg-slate-800 dark:hover:bg-slate-700 dark:text-slate-400
						`}
			>
				Toggle {localStorage.theme === "dark" ? "light" : "dark"} mode
			</button>
		</main>
	);
}
