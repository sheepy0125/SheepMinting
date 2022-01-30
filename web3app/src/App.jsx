import {useState, useEffect} from "react";
import Install from "./components/Installation";
import Home from "./components/Home";

export default function App() {
	// Dark theme
	const [theme, setTheme] = useState("dark");
	useEffect(() => {
		if (localStorage.theme === "dark" || (!("theme" in localStorage) && window.matchMedia("(prefers-color-scheme: dark)").matches)) {
			document.documentElement.classList.add("dark");
		} else {
			document.documentElement.classList.remove("dark");
		}
	}, [theme]);

	function toggleColorScheme() {
		console.log(localStorage.theme);
		localStorage.theme = localStorage.theme === "dark" ? "light" : "dark";
		setTheme(localStorage.theme);
	}

	return (
		<footer className="h-full min-h-screen bg-amber-500 dark:bg-amber-600">
			<div className="flex flex-wrap justify-center gap-8 p-10 h-max">
				<>{window.ethereum ? <Install /> : <Home />}</>
			</div>
			<button
				onClick={toggleColorScheme}
				className={`
						block p-2 mx-auto my-2 bg-indigo-400 rounded-md w-max lg:absolute hover:bg-indigo-300 drop-shadow-xl
						lg:right-2 lg:top-2 text-slate-900 dark:bg-slate-800 dark:hover:bg-slate-700 dark:text-slate-400
					`}
			>
				Toggle {localStorage.theme === "dark" ? "light" : "dark"} mode
			</button>
		</footer>
	);
}
